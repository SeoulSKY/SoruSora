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

import discord

color = discord.Color(0xffd0cf)


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
