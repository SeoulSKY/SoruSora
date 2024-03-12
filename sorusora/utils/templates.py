"""
Provides templates for the Discord bot

Constants:
    color

Functions:
    info()
    success()
    warning()
    error()
"""
import os

import discord
from discord import Locale

from utils import Localization
from utils.constants import BUG_REPORT_URL
from utils.translator import Language

color = discord.Color(0xffd0cf)


async def unknown_error(locale: Locale | Language) -> str:
    """
    Get the message for the unknown error

    :param locale: The language to use
    :return: The message for the unknown error
    """

    loc = Localization(locale, [os.path.join("utils", "templates.ftl")])
    return error(await loc.format_value_or_translate("unknown-error", {"link": BUG_REPORT_URL}))


def info(message: str):
    """
    Convert the message as info message
    :param message: The message to convert
    :return: The converted message
    """
    return ":information_source: " + message


def success(message: str):
    """
    Convert the message as success message
    :param message: The message to convert
    :return: The converted message
    """
    return ":white_check_mark: " + message


def warning(message: str):
    """
    Convert the message as warning message
    :param message: The message to convert
    :return: The converted message
    """
    return ":warning: " + message


def error(message: str):
    """
    Convert the message as error message
    :param message: The message to convert
    :return: The converted message
    """
    return ":x: " + message


def forbidden(message: str):
    """
    Convert the message as forbidden message
    :param message: The message to convert
    :return: The converted message
    """
    return ":no_entry: " + message
