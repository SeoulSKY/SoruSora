"""
Provides list of constants

Constants:
    EMBED_DESCRIPTION_MAX_LENGTH
    MAX_NUM_EMBEDS_IN_MESSAGE
    LANGUAGES
"""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(ROOT_DIR, "..", "cache")
ASSETS_DIR = os.path.join(ROOT_DIR, "..", "assets")

EMBED_DESCRIPTION_MAX_LENGTH = 4096
COMMAND_DESCRIPTION_MAX_LENGTH = 100

MAX_NUM_EMBEDS_IN_MESSAGE = 10

DATABASE_NAME = "SoruSora"
