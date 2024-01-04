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
    "bulgarian",
    "chinese (simplified)",
    "chinese (traditional)",
    "croatian",
    "czech",
    "danish",
    "dutch",
    "english",
    "filipino",
    "finnish",
    "french",
    "german",
    "greek",
    "hindi",
    "hungarian",
    "indonesian",
    "italian",
    "japanese",
    "korean",
    "lithuanian",
    "malay",
    "norwegian",
    "polish",
    "portuguese",
    "romanian",
    "russian",
    "spanish",
    "swedish",
    "thai",
    "turkish",
    "ukrainian",
    "vietnamese",
]

translator = GoogleTranslator()
