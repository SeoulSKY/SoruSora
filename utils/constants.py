"""
Provides list of constants

Classes:
    ErrorCode
    Limit

Constants:
    ROOT_DIR
    CACHE_DIR
    ASSETS_DIR
    BOT_NAME
    DATABASE_NAME
    DEFAULT_LANGUAGE
    BUG_REPORT_LINK
"""

import os
from enum import Enum


class ErrorCode(Enum):
    """
    Provides error codes from discord API
    """
    MESSAGE_EXPIRED = 50027
    MESSAGE_TOO_LONG = 50035

    def __eq__(self, other):
        return self.value == other


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(ROOT_DIR, "..", "cache")
ASSETS_DIR = os.path.join(ROOT_DIR, "..", "assets")
HELP_DIR = os.path.join(ROOT_DIR, "..", "docs", "help")


class Limit(Enum):
    """
    Provides limits from discord API
    """
    EMBED_DESCRIPTION_LEN = 4096
    COMMAND_DESCRIPTION_LEN = 100
    NUM_EMBEDS_IN_MESSAGE = 10

    def __eq__(self, other):
        return self.value == other

    def __lt__(self, other):
        return self.value < other

    def __int__(self):
        return self.value


BOT_NAME = "SoruSora"
DATABASE_NAME = "SoruSora"

DEFAULT_LOCALE = "en"

BUG_REPORT_LINK = "https://github.com/SeoulSKY/SoruSora/issues/new?template=bug_report.md"
