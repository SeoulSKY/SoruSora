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
    MESSAGE_EXPIRED = 50027
    MESSAGE_TOO_LONG = 50035

    def __eq__(self, other):
        return self.value == other


ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = ROOT_DIR.parent / "cache"
ASSETS_DIR = ROOT_DIR.parent / "assets"
HELP_DIR = ROOT_DIR.parent / "docs" / "help"
LOCALES_DIR = ROOT_DIR.parent / "locales"
ABOUT_DIR = ROOT_DIR.parent / "docs" / "about"


class Limit(Enum):
    """
    Provides limits from discord API
    """
    EMBED_DESCRIPTION_LEN = 4096
    COMMAND_NAME_LEN = 32
    COMMAND_DESCRIPTION_LEN = 100
    NUM_EMBEDS_IN_MESSAGE = 10

    def __eq__(self, other):
        return self.value == other

    def __lt__(self, other):
        return self.value < other

    def __int__(self):
        return self.value


languages = {
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
    "pl",
    "pt",
    "ro",
    "ru",
    "es",
    "sv",
    "th",
    "uk",
}


BOT_NAME = "SoruSora"
DATABASE_NAME = "SoruSora"

INVITE_URL = "https://sorusora.seoulsky.org"
GITHUB_URL = "https://github.com/SeoulSKY/SoruSora"
BUG_REPORT_URL = "https://github.com/SeoulSKY/SoruSora/issues/new?template=bug_report.md"
