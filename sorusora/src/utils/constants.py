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
from pathlib import Path


class ErrorCode(Enum):
    """
    Provides error codes from discord API
    """
    MESSAGE_EMPTY = 50006
    MESSAGE_EXPIRED = 50027
    MESSAGE_TOO_LONG = 50035

    def __eq__(self, other):
        return self.value == other


ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
SRC_DIR = ROOT_DIR / "src"
CACHE_DIR = ROOT_DIR / "cache"
ASSETS_DIR = ROOT_DIR / "assets"
DOCS_DIR = ROOT_DIR / "docs"
HELP_DIR = DOCS_DIR / "help"
LOCALES_DIR = ROOT_DIR / "locales"
ABOUT_DIR = DOCS_DIR / "about"


class Limit(Enum):
    """
    Provides limits from discord API
    """
    EMBED_DESCRIPTION_LEN = 4096
    COMMAND_NAME_LEN = 32
    COMMAND_DESCRIPTION_LEN = 100
    NUM_EMBEDS_IN_MESSAGE = 10
    NUM_EMBED_FIELDS = 25
    SELECT_MAX = 25
    NUM_VIEWS_ITEMS = 25

    def __eq__(self, other):
        return self.value == other

    def __lt__(self, other):
        return self.value < other

    def __int__(self):
        return self.value


BOT_NAME = "SoruSora"
DATABASE_NAME = "SoruSora"

INVITE_URL = "https://sorusora.seoulsky.org"
GITHUB_URL = "https://github.com/SeoulSKY/SoruSora"
BUG_REPORT_URL = "https://github.com/SeoulSKY/SoruSora/issues/new?template=bug_report.md"
UNKNOWN_ERROR_FILENAME = "error.log"
