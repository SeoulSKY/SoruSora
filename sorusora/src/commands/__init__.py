"""
This module provides functions to help with the setup of commands

Functions:
    get_resources
    localization_args
    listener
"""

import os
from typing import Any, Coroutine, Callable

from discord.app_commands.commands import Command, ContextMenu, Group

listeners: set[Callable[..., Coroutine]] = set()


def get_resources(command: Command | Group | ContextMenu) -> list[str]:
    """
    Get the resources for a command

    :param command: The command to get resources for
    """

    return [
        os.path.join("context_menus" if isinstance(command, ContextMenu) else "commands", "movie.ftl")
    ]


def localization_args(**extras: Any):
    """
    Decorator to add localization arguments to a command
    """

    def decorator(command: Command | Group | ContextMenu):
        if not isinstance(command, Command | ContextMenu):
            raise TypeError("This decorator must be placed above @app_commands.command()")

        # loc = Localization(DEFAULT_LANGUAGE, get_resources(command))
        # command.name = loc.format_value(f"{command.name.replace('_', '-')}-name")
        # command.description = loc.format_value(f"{command.name.replace('_', '-')}-description")

        for key, value in extras.items():
            command.extras[key.replace("_", "-")] = value

        return command

    return decorator


def listener(func: Callable[..., Coroutine]):
    """
    Decorator to add a listener to the bot
    """

    listeners.add(func)
    return func
