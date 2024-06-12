"""
Provides translator functionality

Classes:
    Language
    Translation
    Localization
    CommandTranslator
    BaseTranslator
    ArgosTranslator
    GoogleTranslator

Functions:
    get_resource
    get_translator
"""

# pylint: disable=too-many-lines

import asyncio
import itertools
import json
import logging
import os
from abc import ABC, abstractmethod
from threading import Lock
from typing import Iterable, AsyncGenerator, Any, Optional, Generator

import argostranslate.package
import argostranslate.translate
import babel
import discord
from deep_translator import GoogleTranslator as Google
from deep_translator.exceptions import TooManyRequests
from discord import Locale, app_commands, AppCommandType
from discord.app_commands import locale_str, TranslationContextTypes, Command, Group, ContextMenu
from discord.ext.commands import Bot
from fluent.runtime import FluentLocalization, FluentResourceLoader
from tqdm import tqdm

from utils.constants import Limit, CACHE_DIR, LOCALES_DIR

logger = logging.getLogger(__name__)


class Language:
    """
    Represents a language
    """

    def __init__(self, locale: Locale | str):
        locale = str(locale)
        self._locale = babel.Locale.parse(locale, sep="-")
        self._code = locale

    def trim_territory(self) -> "Language":
        """
        Trim the territory from the language code

        :return: The language without the territory
        """

        return Language(self.code.split("-", maxsplit=1)[0])

    def has_territory(self) -> bool:
        """
        Check if the language has a territory

        :return: True if the language has a territory
        """

        return "-" in self._code

    @property
    def code(self) -> str:
        """
        Get the language code
        """
        return self._code

    @property
    def name(self) -> str:
        """
        Get the language name
        """
        return self._locale.english_name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Language):
            return False

        return self._locale.language == other._locale.language

    def __str__(self):
        return self.code

    def __hash__(self):
        return hash(self.code)

    def __repr__(self):
        return f"Language({self.code})"


DEFAULT_LANGUAGE = Language("en")


class Translation:
    """
    Represents a translation result
    """

    def __init__(self, source: Language, target: Language, original_text: str, translated_text: str):
        self._source = source
        self._target = target
        self._original_text = original_text
        self._translated_text = translated_text

    @property
    def source(self) -> Language:
        """
        Get the source language
        """
        return self._source

    @property
    def target(self) -> Language:
        """
        Get the target language
        """
        return self._target

    @property
    def original_text(self) -> str:
        """
        Get the original text
        """
        return self._original_text

    @original_text.setter
    def original_text(self, value: str) -> None:
        """
        Set the original text
        """
        self._original_text = value

    @property
    def text(self) -> str:
        """
        Get the translated text
        """
        return self._translated_text

    @text.setter
    def text(self, value: str) -> None:
        """
        Set the translated text
        """
        self._translated_text = value

    def __str__(self) -> str:
        return self._translated_text


class BaseTranslator(ABC):
    """
    Abstract base class for translators
    """

    def __init__(self, supported_languages: Iterable[Language]):
        self._languages = set(supported_languages)
        self._names_to_codes = {language.name: language.code for language in supported_languages}
        self._codes_to_names = {language.code: language.name for language in supported_languages}

    def is_locale_supported(self, locale: Locale) -> bool:
        """
        Check if the locale is supported by the translator

        :param locale: The locale to check
        :return: True if the locale is supported by the translator
        """

        language = Language(locale)

        return self.is_language_supported(language) or self.is_language_supported(language.trim_territory())

    def is_language_supported(self, language: Language) -> bool:
        """
        Check if the language is supported by the translator

        :param language: The language to check
        :return: True if the language is supported by the translator
        """

        return language in self._languages

    def get_supported_languages(self) -> Iterable[Language]:
        """
        Get the supported languages of the translator

        :return: The supported languages of the translator
        """

        return self._languages

    def is_code_supported(self, code: str) -> bool:
        """
        Check if the language code is supported by the translator

        :param code: The language code to check
        :return: True if the language code is supported by the translator
        """

        return code in self._codes_to_names

    def locale_to_language(self, locale: Locale) -> Language:
        """
        Get the language of the locale

        :param locale: The locale to get the language of
        :return: The language of the locale
        :raises ValueError: If the locale is not supported by the translator
        """

        if not self.is_locale_supported(locale):
            raise ValueError(f"Locale {locale} is not supported")

        return Language(locale)

    async def translate_targets(self, text: str, targets: Iterable[Language], source: Language = DEFAULT_LANGUAGE) \
            -> AsyncGenerator[Translation, Any]:
        """
        Translate the text to the target languages

        :param text: The text to translate
        :param targets: The languages to translate to
        :param source: The language to translate from

        :return: The translation
        """
        for target in targets:
            yield await self.translate(text, target, source)

    async def translate_texts(self, texts: Iterable[str], target: Language, source: Language = DEFAULT_LANGUAGE) \
            -> AsyncGenerator[Translation, Any]:
        """
        Translate the texts to the target language

        :param texts: The texts to translate
        :param target: The language to translate to
        :param source: The language to translate from

        :return: The translations
        """
        tasks = []
        for text in texts:
            tasks.append(asyncio.create_task(self.translate(text, target, source)))

        for task in asyncio.as_completed(tasks):
            yield await task

    @abstractmethod
    async def translate(self, text: str, target: Language, source: Language = DEFAULT_LANGUAGE) -> Translation:
        """
        Translate the text to the target language

        :param text: The text to translate
        :param target: The language to translate to
        :param source: The language to translate from

        :return: The translation
        :raises ValueError: If the target or source language is not supported by the translator
        """


class ArgosTranslator(BaseTranslator):
    """
    Translator using Argos Translate
    """

    _CODE_ALIAS = {
        "zh": "zh-CN",
        "zt": "zh-TW",
    }

    _ALIAS_TO_CODE = {v: k for k, v in _CODE_ALIAS.items()}

    _LANGUAGES = None

    def __init__(self):
        if ArgosTranslator._LANGUAGES is None:
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            for package in tqdm(available_packages, "Installing Argos Translate packages", unit="package"):
                argostranslate.package.install_from_path(package.download())

            ArgosTranslator._LANGUAGES = [
                Language(ArgosTranslator._CODE_ALIAS[lang.code]
                         if lang.code in ArgosTranslator._CODE_ALIAS else lang.code)
                for lang in argostranslate.translate.get_installed_languages()
            ]
        super().__init__(ArgosTranslator._LANGUAGES)

    def is_code_supported(self, code: str) -> bool:
        return self.is_language_supported(Language(code) or code in self._CODE_ALIAS)

    def _language_to_code(self, language: Language) -> str:
        return self._ALIAS_TO_CODE[language.code] \
            if language.code in self._ALIAS_TO_CODE else language.trim_territory().code

    async def translate(self, text: str, target: Language, source: Language = DEFAULT_LANGUAGE) -> Translation:
        if not self.is_language_supported(target):
            raise ValueError(f"Language {target} is not supported")
        if not self.is_language_supported(source):
            raise ValueError(f"Language {source} is not supported")

        if source == target or text.isspace():
            result = text
        else:
            try:
                result = await asyncio.to_thread(
                    argostranslate.translate.translate,
                    text,
                    self._language_to_code(source),
                    self._language_to_code(target)
                )
            except Exception as ex:
                raise ValueError(f"Failed to translate text '{text}' from `{source}` to `{target}`") from ex

        return Translation(source, target, text, result)


class GoogleTranslator(BaseTranslator):
    """
    Translator using Google Translate
    """

    _LANGUAGES = set()
    for code in Google().get_supported_languages(as_dict=True).values():
        try:
            _LANGUAGES.add(Language(code))
        except babel.core.UnknownLocaleError:
            pass

    def __init__(self):
        super().__init__(self._LANGUAGES)

        self._fallback_translator = ArgosTranslator()

    def get_supported_languages(self) -> Iterable[Language]:
        return self._languages.intersection(self._fallback_translator.get_supported_languages())

    def is_code_supported(self, code: str) -> bool:
        return super().is_code_supported(code) and self._fallback_translator.is_code_supported(code)

    def is_locale_supported(self, locale: Locale) -> bool:
        return super().is_locale_supported(locale) and self._fallback_translator.is_locale_supported(locale)

    def is_language_supported(self, language: Language) -> bool:
        return super().is_language_supported(language) and self._fallback_translator.is_language_supported(language)

    def _language_to_code(self, language: Language) -> str:
        return language.code if self.is_language_supported(language) else language.trim_territory().code

    async def translate(self, text: str, target: Language, source: Language = DEFAULT_LANGUAGE) -> Translation:
        try:
            return Translation(
                source,
                target,
                text,
                await asyncio.to_thread(
                    Google(self._language_to_code(source), self._language_to_code(target)).translate,
                    text
                )
            )
        except TooManyRequests:
            return await self._fallback_translator.translate(text, target, source)

    async def translate_texts(self, texts: Iterable[str], target: Language, source: Language = DEFAULT_LANGUAGE
                              ) -> AsyncGenerator[Translation, Any]:
        texts = list(texts)
        try:
            translations = await asyncio.to_thread(
                Google(self._language_to_code(source), self._language_to_code(target)).translate_batch,
                texts
            )
        except TooManyRequests:
            async for translation in self._fallback_translator.translate_texts(texts, target, source):
                yield translation

            return

        for i, translation in enumerate(translations):
            yield Translation(source, target, texts[i], translation)


def get_translator() -> BaseTranslator:
    """
    Create a translator
    """

    return GoogleTranslator()


class Cache:
    """
    Provides caching functionality
    """
    # pylint: disable=unsupported-membership-test
    # pylint: disable=unsubscriptable-object
    # pylint: disable=unsupported-assignment-operation

    PATH = CACHE_DIR / "translations.json"

    _data: Optional[dict[str, dict[str, str]]] = None
    _lock = Lock()

    def __init__(self):
        raise TypeError("This class cannot be instantiated")

    @classmethod
    def _load(cls) -> None:
        os.makedirs(CACHE_DIR, exist_ok=True)

        with cls._lock:
            try:
                with open(cls.PATH, "r", encoding="utf-8") as file:
                    cls._data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                cls._data = {}

    @classmethod
    async def save(cls) -> None:
        """
        Save the cache to the file
        """

        if cls._data is None:
            return

        with cls._lock:
            with open(cls.PATH, "w", encoding="utf-8") as file:
                await asyncio.to_thread(json.dump, cls._data, file)

        cls._data = None

    @classmethod
    def has(cls, language: Language, text: str) -> bool:
        """
        Check if the translation is in the cache

        :param language: The language of the translation
        :param text: The text to translate
        :return: True if the translation is in the cache
        """

        if cls._data is None:
            cls._load()

        with cls._lock:
            code = language.code
            if language.code not in cls._data:
                code = language.trim_territory().code

            return code in cls._data and text in cls._data[code]

    @classmethod
    def get(cls, language: Language, text: str) -> Translation:
        """
        Get the translation from the cache

        :param language: The language of the translation
        :param text: The text to translate
        :raises ValueError: If the translation is not found

        :return: The translation
        """

        if cls._data is None:
            cls._load()

        try:
            with cls._lock:
                code = language.code
                if language.code not in cls._data:
                    code = language.trim_territory().code

                return Translation(DEFAULT_LANGUAGE, language, text, cls._data[code][text])
        except KeyError as ex:
            raise ValueError(f"Translation of text '{text}' not found for language '{language}'") from ex

    @classmethod
    def set(cls, translation: Translation) -> None:
        """
        Set the translation to the cache

        :param translation: The translation to set
        """

        if cls._data is None:
            cls._load()

        with cls._lock:
            if translation.target.code not in cls._data:
                cls._data[translation.target.code] = {}

            cls._data[translation.target.code][translation.original_text] = translation.text

    @classmethod
    def remove(cls, language: Language, text: str) -> None:
        """
        Remove the translation from the cache

        :param language: The language of the translation
        :param text: The text to translate
        """

        if cls._data is None:
            cls._load()

        with cls._lock:
            if language.code in cls._data:
                cls._data[language.code].pop(text, None)


class Localization:
    """
    Provides localization functionality
    """

    _loader = FluentResourceLoader(os.path.join(LOCALES_DIR, "{locale}"))

    _translator: BaseTranslator = GoogleTranslator()

    def __init__(self, locale: Locale | Language, resources: list[str] = None, fallbacks: Optional[list[str]] = None):
        """
        Create a localization

        :param locale: The locale of the localization
        :param resources: The paths to .ftl files inside locales folder
        :param fallbacks: The fallbacks of the language code used if the locale is not found
        """
        self._language = Language(str(locale)) if isinstance(locale, Locale) else locale

        if resources is None:
            resources = []
        if fallbacks is None:
            fallbacks = []

        resources.append(self.get_resource())

        if self._language.has_territory():
            fallbacks.append(self._language.trim_territory().code)

        if not self._translator.is_language_supported(self._language):
            fallbacks.append(DEFAULT_LANGUAGE.code)

        self._loc = FluentLocalization([self._language.code] + fallbacks, resources, self._loader)

    @staticmethod
    def get_resource() -> str:
        """
        Get the resource of the localization

        :return: The resources of the localization
        """

        return os.path.join("utils", "translator.ftl")

    @staticmethod
    def has(locale: Locale | str) -> bool:
        """
        Check if the locale has localization

        :param locale: The locale or code to check
        :return: True if the locale has localization
        """

        language = Language(locale)

        return (os.path.exists(LOCALES_DIR / language.code) or
                os.path.exists(LOCALES_DIR / language.trim_territory().code))

    @property
    def language(self) -> Language:
        """
        Get the language of the localization
        """

        return self._language

    def _format_value(self, msg_id: str, args: Optional[dict[str, Any]] = None) -> Optional[str]:
        result = self._loc.format_value(msg_id, args)
        return result if result != msg_id else None  # format_value() returns msg_id if not found

    def format_value(self, msg_id: str, args: Optional[dict[str, Any]] = None) -> str:
        """
        Format the value of the message id with the arguments.

        :param msg_id: The message id to format
        :param args: The arguments to format the message with
        :return: The formatted message
        :raises ValueError: If the message id is not found
        """

        result = self._format_value(msg_id, args)
        if result is None:
            raise ValueError(f"Localization '{self._loc.locales[0]}' not found for message id '{msg_id}' in resources"
                             f" '{self._loc.resource_ids}'")

        return result

    async def format_value_or_translate(self, msg_id: str, args: Optional[dict[str, Any]] = None) -> str:
        """
        Format the value of the message id with the arguments, or translate the value if message id is not found

        :param msg_id: The message id to format
        :param args: The arguments to format the message with
        :return: The formatted message
        """

        result = self._format_value(msg_id, args)
        if result is not None:
            return result

        loc = Localization(DEFAULT_LANGUAGE, self.resources)
        text = loc.format_value(msg_id, args)

        if not Cache.has(self._language, text):
            translation = await self._translator.translate(text, self._language)
            Cache.set(translation)
            await Cache.save()

        return Cache.get(self._language, text).text

    @property
    def locales(self) -> list[str]:
        """
        Get the locales of the localization

        :return: The locales of the localization
        """

        return self._loc.locales

    @property
    def resources(self) -> list[str]:
        """
        Get the resources of the localization

        :return: The resources of the localization
        """

        return self._loc.resource_ids


def format_localization(**kwargs: Any):
    """
    Format the localization of the command

    :param kwargs: The arguments for formatting
    """

    def decorator(command: Command | ContextMenu) -> Command | Group | ContextMenu:
        if not isinstance(command, (Command, ContextMenu)):
            raise TypeError("This decorator must be placed above @app_commands.command or @app_commands.context_menu")

        for key, value in kwargs.items():
            command.extras[key.replace("_", "-")] = value

        return command

    return decorator


class CommandTranslator(discord.app_commands.Translator):
    """
    Translator for the commands
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

        self._translator: BaseTranslator = GoogleTranslator()

    @staticmethod
    def _get_args(command: Command | ContextMenu) -> dict[str, Any]:
        """
        Get the arguments for the command

        :param command: The command to get the arguments from
        :return: The arguments for the command
        """

        return command.extras

    async def load(self):
        localized: set[Language] = set()
        non_localized: set[Language] = set()

        for language in map(lambda x: Language(str(x)), Locale):
            target = localized if Localization.has(language.code) else non_localized
            target.add(language)

        coros = [
            self._translate_about_docs(non_localized),
            self._translate_help_docs(non_localized),
            self._translate_commands(non_localized),
            self._localize_about_docs(localized),
            self._localize_help_docs(localized),
            self._localize_commands(localized)
        ]

        for coro in coros:
            await coro

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContextTypes) -> Optional[str]:
        language = Language(locale)
        if language == DEFAULT_LANGUAGE:
            return string.message

        if Cache.has(language, string.message):
            return Cache.get(language, string.message).text

        logger.warning("Translation of text '%s' not found for locale '%s'", string.message, locale)
        return None

    async def _translate_about_docs(self, languages: Iterable[Language]) -> None:
        # pylint: disable=import-outside-toplevel
        from commands.about import get_about_dir

        pbar = tqdm(desc="Translating about documents", total=0, unit="language")
        with open(get_about_dir(DEFAULT_LANGUAGE), "r", encoding="utf-8") as file:
            text = file.read()

        targets = []
        for language in languages:
            if not Cache.has(language, text):
                targets.append(language)
                pbar.total += 1

        if len(targets) == 0:
            return

        async for translation in self._translator.translate_targets(text, targets):
            Cache.set(translation)
            pbar.update()

        pbar.close()

        await Cache.save()

    def _get_commands(self) -> Generator[Command, Any, None]:
        # pylint: disable=import-outside-toplevel
        from commands.help_ import help_, HIDDEN_COMMANDS

        for command in self.bot.tree.walk_commands():
            if (command.qualified_name == help_.qualified_name or isinstance(command, app_commands.Group) or
                    type(command.root_parent if command.root_parent else command) in HIDDEN_COMMANDS):
                continue

            yield command

    @staticmethod
    async def _localize_about_docs(languages: Iterable[Language]) -> None:
        # pylint: disable=import-outside-toplevel
        from commands.about import get_about_dir

        with open(get_about_dir(DEFAULT_LANGUAGE), "r", encoding="utf-8") as file:
            default_text = file.read()

        for language in tqdm(languages, desc="Localizing about documents", total=0, unit="language"):
            try:
                with open(get_about_dir(language), "r", encoding="utf-8") as file:
                    text = file.read()
            except FileNotFoundError:
                with open(get_about_dir(language.trim_territory()), "r", encoding="utf-8") as file:
                    text = file.read()

            if not Cache.has(language, default_text):
                Cache.set(Translation(
                    DEFAULT_LANGUAGE,
                    language,
                    default_text,
                    text
                ))

        await Cache.save()

    async def _localize_help_docs(self, languages: Iterable[Language]) -> None:
        # pylint: disable=import-outside-toplevel
        from commands.help_ import get_help_dir

        for language in tqdm(languages, desc="Localizing help documents", total=0, unit="language"):
            for command in self._get_commands():
                with open(get_help_dir(command.qualified_name, DEFAULT_LANGUAGE), "r", encoding="utf-8") as file:
                    default_text = file.read()

                try:
                    with open(get_help_dir(command.qualified_name, language), "r", encoding="utf-8") as file:
                        text = file.read()
                except FileNotFoundError:
                    with (open(get_help_dir(command.qualified_name, language.trim_territory()), "r", encoding="utf-8")
                          as file):
                        text = file.read()

                if not Cache.has(language, default_text):
                    Cache.set(Translation(
                        DEFAULT_LANGUAGE,
                        language,
                        default_text,
                        text
                    ))

        await Cache.save()

    async def _translate_help_docs(self, languages: Iterable[Language]) -> None:
        # pylint: disable=import-outside-toplevel
        from commands.help_ import get_help_dir

        async def translate_texts(texts: list[str], language: Language) -> list[Translation]:
            translations = []
            async for translation in self._translator.translate_texts(texts, language):
                translations.append(translation)

            return translations

        tasks = []
        pbar = tqdm(desc="Translating help documents", total=0, unit="language")
        for language in languages:
            texts = []

            for command in self._get_commands():
                with open(get_help_dir(command.qualified_name, DEFAULT_LANGUAGE), "r", encoding="utf-8") as file:
                    text = file.read()

                if not Cache.has(language, text):
                    texts.append(text)

            if len(texts) == 0:
                continue

            tasks.append(asyncio.create_task(translate_texts(texts, language)))
            pbar.total += 1

        for task in asyncio.as_completed(tasks):
            for translation in await task:
                Cache.set(translation)

            pbar.update()

        pbar.close()

        await Cache.save()

    async def _localize_commands(self, languages: Iterable[Language]) -> None:
        def _localize(loc: Localization, args: dict[str, Any], msg_id: str, is_name: bool) -> str:
            result = loc.format_value(msg_id, args)
            transformed = "".join(char for char in result
                                  if char.isalnum()).lower().replace(" ", "_") \
                if is_name else result

            return transformed[:int(Limit.COMMAND_DESCRIPTION_LEN)]

        for language in tqdm(languages, desc="Localizing commands", total=0, unit="language"):
            for command in self.bot.tree.walk_commands():
                if isinstance(command, Group):
                    continue

                loc = Localization(language, [
                    os.path.join("commands",
                                 f"{command.root_parent.name if command.root_parent else command.name}.ftl"),
                    Localization.get_resource()
                ])

                command_prefix = command.name.replace('_', '-')

                Cache.set(Translation(
                    DEFAULT_LANGUAGE,
                    language,
                    command.name,
                    _localize(loc, self._get_args(command), f"{command_prefix}-name", True)
                ))

                Cache.set(Translation(
                    DEFAULT_LANGUAGE,
                    language,
                    command.description,
                    _localize(loc, self._get_args(command), f"{command_prefix}-description", False)
                ))

                if isinstance(command, app_commands.Group):
                    continue

                for name, description, choices in [(param.name, param.description, param.choices)
                                                   for param in command.parameters]:
                    replaced_name = name.replace("_", "-")

                    Cache.set(Translation(
                        DEFAULT_LANGUAGE,
                        language,
                        name,
                        _localize(loc, self._get_args(command), f"{command_prefix}-{replaced_name}-name", True)
                    ))

                    Cache.set(Translation(
                        DEFAULT_LANGUAGE,
                        language,
                        description,
                        _localize(loc, self._get_args(command), f"{command_prefix}-{replaced_name}-description",
                                  False)
                    ))

                    for choice in choices:
                        Cache.set(Translation(
                            DEFAULT_LANGUAGE,
                            language,
                            choice.name,
                            choice.value if choice.name.isnumeric() else _localize(loc, self._get_args(command),
                                                                                   choice.value, False)
                        ))

            for context_menu in itertools.chain(self.bot.tree.walk_commands(type=AppCommandType.message),
                                                self.bot.tree.walk_commands(type=AppCommandType.user)):
                loc = Localization(language, [os.path.join(
                    "context_menus", f"{context_menu.name.lower().replace(' ', '_')}.ftl"
                )])
                Cache.set(Translation(
                    DEFAULT_LANGUAGE,
                    language,
                    context_menu.name,
                    _localize(loc, self._get_args(context_menu),
                              f"{context_menu.name.lower().replace(' ', '-')}-name", False)
                ))

        await Cache.save()

    async def _translate_commands(self, languages: Iterable[Language]) -> None:
        # pylint: disable=too-many-locals
        """
        Translate the commands to given locales
        """

        async def translate_texts(language: Language, texts: list[str], is_name: list[bool]
                                  ) -> Iterable[Translation]:
            translations = []
            async for translation in self._translator.translate_texts(
                    map(lambda x: x.replace("_", " "), texts), language):
                translations.append(translation)

            for i, translation in enumerate(translations):
                if is_name[i]:
                    translation.original_text = texts[i]
                    translation.text = ("".join(char for char in translation.text if char.isalnum())
                                        .lower().replace(" ", "_")[:int(Limit.COMMAND_NAME_LEN)])
                else:
                    translation.text = translation.text[:int(Limit.COMMAND_DESCRIPTION_LEN)]

            return translations

        tasks = []
        pbar = tqdm(desc="Translating commands", total=0, unit="language")

        for language in languages:
            texts = []
            is_name = []

            for command in self.bot.tree.walk_commands():
                texts.append(command.name)
                is_name.append(True)

                texts.append(command.description)
                is_name.append(False)

                if isinstance(command, app_commands.Group):
                    continue

                for param in command.parameters:
                    texts.append(param.name)
                    is_name.append(True)

                    texts.append(param.description)
                    is_name.append(False)

                    for choice in param.choices:
                        texts.append(choice.name)
                        is_name.append(False)

            for context_menu in itertools.chain(self.bot.tree.walk_commands(type=AppCommandType.message),
                                                self.bot.tree.walk_commands(type=AppCommandType.user)):
                texts.append(context_menu.name)
                is_name.append(False)

            target_texts = []
            target_is_name = []
            for text, name in zip(texts, is_name):
                if Cache.has(language, text):
                    continue

                target_texts.append(text)
                target_is_name.append(name)

            if len(target_texts) == 0:
                continue

            tasks.append(asyncio.create_task(translate_texts(language, target_texts, target_is_name)))
            pbar.total += 1

        for task in asyncio.as_completed(tasks):
            for translation in await task:
                Cache.set(translation)

            pbar.update()

        pbar.close()

        await Cache.save()
