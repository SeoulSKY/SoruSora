"""
Provides list of constants

Constants:
    EMBED_DESCRIPTION_MAX_LENGTH
    MAX_NUM_EMBEDS_IN_MESSAGE
    LANGUAGES
"""

from deep_translator import GoogleTranslator

EMBED_DESCRIPTION_MAX_LENGTH = 4096

MAX_NUM_EMBEDS_IN_MESSAGE = 10

languages = [
    "chinese (simplified)",
    "chinese (traditional)",
    "english",
    "filipino",
    "french",
    "german",
    "indonesian",
    "italian",
    "japanese",
    "korean",
    "malay",
    "russian",
    "spanish",
    "thai",
    "vietnamese",
]

translator = GoogleTranslator()
