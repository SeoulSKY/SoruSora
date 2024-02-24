"""
Provides translator functionality

Classes:
    Localization
    CommandTranslator
    BatchTranslator

Functions:
    has_localization
    get_resource
    translate
    is_default
    language_to_code
    code_to_language
    locale_to_code
    locale_to_language

Constants:
    languages
    Translator
    locales
"""
import concurrent
import itertools
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Type, Optional, Any, Union, Iterable

import discord
import langid
from deep_translator import GoogleTranslator
from deep_translator.base import BaseTranslator
from discord import Locale, app_commands, AppCommandType
from discord.app_commands import locale_str, TranslationContextTypes
from discord.app_commands.translator import TranslationContextLocation
from discord.ext.commands import Bot
from fluent.runtime import FluentResourceLoader, FluentLocalization
from tqdm import tqdm

from utils.constants import DEFAULT_LOCALE, Limit

languages = [
    "zh-CN",
    "zh-TW",
    "nl",
    "en",
    "tl",
    "fr",
    "de",
    "el",
    "hi",
    "id",
    "it",
    "ja",
    "ko",
    "ms",
    "no",
    "pl",
    "pt",
    "ro",
    "ru",
    "es",
    "sv",
    "th",
    "uk",
    "vi",
]


Translations = dict[str, dict[str, str]]
Translator: Type[BaseTranslator] = GoogleTranslator
_translator = Translator()

for lang in languages:
    assert _translator.is_language_supported(lang), f"'{lang}' is not a supported language"

_LANGUAGES_TO_CODES = _translator.get_supported_languages(as_dict=True)
_CODES_TO_LANGUAGES = {v: k for k, v in _LANGUAGES_TO_CODES.items()}

logger = logging.getLogger(__name__)


def translator_code(code: str) -> str:
    """
    Convert the language code to the code for translators

    :param code: The language code to convert
    :return: The translator code
    """

    return code.split("-")[0]


def has_localization(locale: str) -> bool:
    """
    Check if the locale has localization

    :param locale: The locale to check
    :return: True if the locale has localization
    """

    return os.path.exists(os.path.join("locales", locale))


def get_resource() -> str:
    """
    Get the resource for the translator
    """

    return os.path.join("utils", "translator.ftl")


def translate(text: str, target: Union[str, Locale], source: str = "auto") -> str:
    """
    Translate the text to the target language

    :param text: The text to translate
    :param target: The language to translate to
    :param source: The language to translate from
    :return: The translated text
    """

    if isinstance(target, Locale):
        target = locale_to_code(target)

    return Translator(source, target).translate(text)


def is_default(code: str) -> bool:
    """
    Check if the language code is a default locale

    :param code: The language code to check
    :return: True if the language code is a default locale
    """

    return code.startswith(DEFAULT_LOCALE)


def language_to_code(language: str) -> str:
    """
    Get the language code of the language

    :param language: The language to get the code of
    :return: The language code of the language
    :raises ValueError: If the language is not supported by the translator
    """

    if language not in _LANGUAGES_TO_CODES:
        raise ValueError(f"Language {language} is not supported")

    return _LANGUAGES_TO_CODES[language]


def code_to_language(code: str) -> str:
    """
    Get the language of the language code

    :param code: The language code to get the language of
    :return: The language of the language code
    :raises ValueError: If the language code is not supported by the translator
    """

    if code not in _CODES_TO_LANGUAGES:
        code = translator_code(code)

        if code not in _CODES_TO_LANGUAGES:
            raise ValueError(f"Language code {code} is not supported")

    return _CODES_TO_LANGUAGES[code]


def locale_to_code(locale: Locale) -> str:
    """
    Get the language code of the locale

    :param locale: The locale to get the string representation
    :return: The language code of the locale
    :raises ValueError: If the locale is not supported by the translator
    """

    language_code = str(locale)
    if _translator.is_language_supported(language_code):
        return language_code

    language_code = translator_code(language_code)

    if _translator.is_language_supported(language_code):
        return language_code

    raise ValueError(f"Locale {locale} is not supported")


def locale_to_language(locale: Locale) -> str:
    """
    Get the language of the locale

    :param locale: The locale to get the language of
    :return: The language of the locale
    :raises ValueError: If the locale is not supported by the translator
    """

    return _CODES_TO_LANGUAGES[locale_to_code(locale)]


class Localization:
    """
    Provides localization functionality
    """

    _loader = FluentResourceLoader(os.path.join("locales", "{locale}"))

    _cache = {}
    _cache_lock = Lock()

    def __init__(self, locale: Union[str, Locale], resources: list[str], fallbacks: Optional[list[str]] = None):
        if len(resources) == 0:
            raise ValueError("At least one resource must be provided")

        if isinstance(locale, Locale):
            locale = locale_to_code(locale)

        locales = [locale]
        if fallbacks is not None:
            locales.extend(fallbacks)

        self._loc = FluentLocalization(locales, resources, self._loader)

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

    def format_value_or_translate(self, msg_id: str, args: Optional[dict[str, Any]] = None) -> str:
        """
        Format the value of the message id with the arguments, or translate the message id if not found

        :param msg_id: The message id to format
        :param args: The arguments to format the message with
        :return: The formatted message
        """

        with self._cache_lock:
            if msg_id in self._cache:
                return self._cache[msg_id]

        result = self._format_value(msg_id, args)
        if result is not None:
            return result

        loc = Localization(DEFAULT_LOCALE, self._loc.resource_ids)
        translated = translate(loc.format_value(msg_id, args), self._loc.locales[0], DEFAULT_LOCALE)

        with self._cache_lock:
            self._cache[msg_id] = translated

        return translated

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


class CommandTranslator(discord.app_commands.Translator):
    """
    Translator for the commands
    """

    _CACHING_TRANSLATIONS = {
        TranslationContextLocation.command_name,
        TranslationContextLocation.command_description,
        TranslationContextLocation.group_name,
        TranslationContextLocation.group_description,
        TranslationContextLocation.other,
    }

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

        self._translations = {}

    async def load(self) -> None:
        localized = set()
        non_localized = set()

        for locale in map(locale_to_code, Locale):
            if locale == DEFAULT_LOCALE:
                continue

            if has_localization(locale):
                localized.add(locale)
            else:
                non_localized.add(locale)

        self._translations = self._translate_commands(non_localized)
        localizations = self._localize_commands(localized)

        for locale, localization in localizations.items():
            self._translations[locale] = localization

    async def unload(self) -> None:
        self._translations.clear()

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContextTypes) -> Optional[str]:
        locale = locale_to_code(locale)
        if is_default(locale):
            return string.message
        if locale in self._translations and string.message in self._translations[locale]:
            translation = self._translations[locale][string.message]
            if context.location not in self._CACHING_TRANSLATIONS:
                self._translations[locale].pop(string.message)
            return translation

        logger.warning("Translation of text '%s' not found for locale '%s'", string.message, locale)
        return None

    def _localize_commands(self, locales: Iterable[str]) -> Translations:
        localizations = {}

        def localize(loc: Localization, args: dict, msg_id: str, snake_case: bool) -> str:
            result = loc.format_value(msg_id, args)
            transformed = "".join(char for char in result
                                  if char.isalnum()).lower().replace(" ", "_") \
                if snake_case else result

            return transformed[:int(Limit.COMMAND_DESCRIPTION_LEN)]

        for locale in tqdm(locales, desc="Localizing commands", unit="locale"):
            localization = {}

            for command in self.bot.tree.walk_commands():
                loc = Localization(locale, [
                    os.path.join("commands",
                                 f"{command.root_parent.name if command.root_parent else command.name}.ftl"),
                    get_resource()
                ])

                command_prefix = command.name.replace('_', '-')

                localization[command.name] = localize(loc, command.extras,
                                                      f"{command_prefix}-name", True)
                localization[command.description] = localize(loc, command.extras,
                                                             f"{command_prefix}-description", False)

                if isinstance(command, app_commands.Group):
                    continue

                for name, description, choices in [(param.name, param.description, param.choices)
                                                   for param in command.parameters]:
                    replaced_name = name.replace('_', '-')
                    localization[name] = localize(loc, command.extras, f"{command_prefix}-{replaced_name}-name",
                                                  True)
                    localization[description] = localize(loc, command.extras,
                                                         f"{command_prefix}-{replaced_name}-description",
                                                         False)

                    for choice in choices:
                        if choice.name.isnumeric():
                            localization[choice.name] = choice.value
                        else:
                            localization[choice.name] = localize(loc, command.extras, choice.value, False)

            for context_menu in itertools.chain(self.bot.tree.walk_commands(type=AppCommandType.message),
                                                self.bot.tree.walk_commands(type=AppCommandType.user)):
                loc = Localization(locale, [os.path.join(
                    "context_menus", f"{context_menu.name.lower().replace(' ', '_')}.ftl"
                )])

                localization[context_menu.name] = localize(loc, context_menu.extras,
                                                           f"{context_menu.name.lower().replace(' ', '-')}-name",
                                                           False)

            localizations[locale] = localization

        return localizations

    def _translate_commands(self, locales: Iterable[str]) -> Translations:
        """
        Translate the commands to given locales
        """

        translations = {}
        lock = Lock()
        pbar = tqdm(total=0, desc="Translating commands", unit="locale")

        def translate_batch(locale: str, texts: list[str], snake_case: list[bool]) -> None:
            with lock:
                pbar.total += 1

            translated = (Translator(DEFAULT_LOCALE, locale)
                          .translate_batch(list(map(lambda x: x.replace("_", " "), texts))))

            for i, text in enumerate(texts):
                result = "".join(char for char in translated[i]
                                 if char.isalnum()).lower().replace(" ", "_"
                                                                    ) if snake_case[i] else translated[i]
                with lock:
                    translations[locale][text] = result[:int(Limit.COMMAND_DESCRIPTION_LEN)]
                    pbar.update()
                    pbar.set_description(f"Translated commands ({locale})")

        with ThreadPoolExecutor() as executor:
            for locale in locales:
                translations[locale] = {}

                batch = []
                snake_cases = []
                for command in self.bot.tree.walk_commands():
                    batch.append(command.name)
                    snake_cases.append(True)

                    batch.append(command.description)
                    snake_cases.append(False)

                    if isinstance(command, app_commands.Group):
                        continue

                    for param in command.parameters:
                        batch.append(param.name)
                        snake_cases.append(True)

                        batch.append(param.description)
                        snake_cases.append(False)

                        batch.extend(choice.name for choice in param.choices)
                        snake_cases.extend(itertools.repeat(False, len(param.choices)))

                for context_menu in itertools.chain(self.bot.tree.walk_commands(type=AppCommandType.message),
                                                    self.bot.tree.walk_commands(type=AppCommandType.user)):
                    batch.append(context_menu.name)
                    snake_cases.append(False)

                executor.submit(translate_batch, locale, batch, snake_cases)

            executor.shutdown(wait=True)

        return translations


# pylint: disable=too-few-public-methods
class BatchTranslator:
    """
    Translator that can translate a text to multiple languages concurrently
    """

    def __init__(self, targets: list[str]):
        self._translators = (Translator(target=target) for target in targets)
        self._executor = ThreadPoolExecutor(max_workers=len(targets))

    async def translate(self, text: str, source: Optional[str] = None):
        """
        Translate the text to target languages

        :param text: The text to translate
        :param source: The language of the text
        :return: List of tuples containing translated language and text
        """

        if source is None:
            source, _ = langid.classify(text)

        futures = []
        for translator in self._translators:
            if source == translator.target:
                continue

            translator.source = source
            futures.append(self._executor.submit(self._translate, text, translator))

        for future in concurrent.futures.as_completed(futures):
            yield future.result()

    @staticmethod
    def _translate(text: str, translator: Translator) -> tuple[str, str]:
        return _CODES_TO_LANGUAGES[translator.target], translator.translate(text)
