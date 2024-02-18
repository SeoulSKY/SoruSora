"""
Provides translator functionality

Classes:
    CommandTranslator
    BatchTranslator

Functions:
    language_to_code
    locale_to_code

Constants:
    languages
    Translator
"""

import concurrent
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Type, Optional

import discord
import langid
from deep_translator import GoogleTranslator
from deep_translator.base import BaseTranslator
from discord import Locale
from discord.app_commands import locale_str, TranslationContextTypes

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
    assert _translator.is_language_supported(lang), f"{lang} is not a supported language"

_LANGUAGES_TO_CODES = _translator.get_supported_languages(as_dict=True)
_CODES_TO_LANGUAGES = {v: k for k, v in _LANGUAGES_TO_CODES.items()}

logger = logging.getLogger(__name__)


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
