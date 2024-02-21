"""
Provides translator functionality

Classes:
    Localization
    CommandTranslator
    BatchTranslator

Functions:
    translate
    is_english
    language_to_code
    locale_to_code
    locale_to_language

Constants:
    languages
    Translator
    locales
"""

import concurrent
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Type, Optional, Any

import discord
import langid
from deep_translator import GoogleTranslator
from deep_translator.base import BaseTranslator
from discord import Locale
from discord.app_commands import locale_str, TranslationContextTypes
from fluent.runtime import FluentResourceLoader, FluentLocalization

languages = [
    "chinese (simplified)",
    "chinese (traditional)",
    "dutch",
    "english",
    "filipino",
    "finnish",
    "french",
    "german",
    "greek",
    "hindi",
    "indonesian",
    "italian",
    "japanese",
    "korean",
    "malay",
    "norwegian",
    "polish",
    "portuguese",
    "romanian",
    "russian",
    "spanish",
    "swedish",
    "thai",
    "ukrainian",
    "vietnamese",
]

Translator: Type[BaseTranslator] = GoogleTranslator
_translator = Translator()

for lang in languages:
    assert _translator.is_language_supported(lang), f"'{lang}' is not a supported language"

_LANGUAGES_TO_CODES = _translator.get_supported_languages(as_dict=True)
_CODES_TO_LANGUAGES = {v: k for k, v in _LANGUAGES_TO_CODES.items()}

logger = logging.getLogger(__name__)


class Localization:
    """
    Provides localization functionality
    """

    _loader = FluentResourceLoader(os.path.join("locales", "{locale}"))

    def __init__(self, locales: list[str], resources: list[str]):
        self._localization = FluentLocalization(locales, resources, self._loader)

    def format_value(self, msg_id: str, args: Optional[dict[str, Any]] = None) -> str:
        """
        Format the value of the message id with the arguments. If the message id is not found, translate it to the first
        locale

        :param msg_id: The message id to format
        :param args: The arguments to format the message with
        :return: The formatted message
        """

        text = self._localization.format_value(msg_id, args)
        if text != msg_id:  # format_value() returns msg_id if not found
            return text

        return translate(text, self._localization.locales[0])

    @property
    def locales(self) -> list[str]:
        """
        Get the locales of the localization

        :return: The locales of the localization
        """

        return self._localization.locales

    @property
    def resources(self) -> list[str]:
        """
        Get the resources of the localization

        :return: The resources of the localization
        """

        return self._localization.resource_ids


def translate(text: str, target: str, source: str = "auto") -> str:
    """
    Translate the text to the target language

    :param text: The text to translate
    :param target: The language to translate to
    :param source: The language to translate from
    :return: The translated text
    """

    return Translator(source, target).translate(text)


def is_english(code: str) -> bool:
    """
    Check if the language code is English

    :param code: The language code to check
    :return: True if the language code is English
    """

    return code.startswith("en")


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

    # try again with characters after '-' truncated
    language_code = language_code.split("-", maxsplit=1)[0]
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


class CommandTranslator(discord.app_commands.Translator):
    """
    Translator for the commands
    """

    def __init__(self, cache: dict[Locale, dict[str, str]] = None):
        super().__init__()
        self._cache = cache or {}

    async def translate(self, string: locale_str, locale: Locale, context: TranslationContextTypes) -> Optional[str]:
        if locale in {Locale.british_english, Locale.american_english}:
            return None
        if locale in self._cache and string.message in self._cache[locale]:
            return self._cache[locale][string.message]

        logger.warning("Translation of text '%s' not found for locale '%s'", string.message, locale)
        return None


# pylint: disable=too-few-public-methods
class BatchTranslator:
    """
    Translator that can translate a text to multiple languages concurrently
    """

    def __init__(self, targets: list[str]):
        self._translators = (Translator(target=target) for target in targets)
        self._executor = ThreadPoolExecutor(max_workers=len(targets))

    async def translate(self, text: str):
        """
        Translate the text to target languages

        :param text: The text to translate
        :return: List of tuples containing target language and translated text
        """

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
