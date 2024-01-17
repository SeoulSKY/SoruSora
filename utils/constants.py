"""
Provides list of constants

Constants:
    EMBED_DESCRIPTION_MAX_LENGTH
    MAX_NUM_EMBEDS_IN_MESSAGE
    LANGUAGES
"""

import os
from typing import Type

from deep_translator import GoogleTranslator
from deep_translator.base import BaseTranslator

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(ROOT_DIR, "..", "cache")
ASSETS_DIR = os.path.join(ROOT_DIR, "..", "assets")

EMBED_DESCRIPTION_MAX_LENGTH = 4096

MAX_NUM_EMBEDS_IN_MESSAGE = 10

DATABASE_NAME = "SoruSora"

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
translator = Translator()
