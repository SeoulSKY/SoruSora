"""
This module sets up the program and provides functions to help with the setup

Functions:
    get_commands
"""

import os
import sys
from importlib import import_module

import discord
from discord import app_commands
from discord.app_commands import Group, Command, ContextMenu
from dotenv import load_dotenv

from commands.movie import Movie
from utils.constants import SRC_DIR, ROOT_DIR

load_dotenv()

sys.path.append(os.path.join(ROOT_DIR, "src"))  # Add the src directory to the path
sys.path.append(os.path.join(ROOT_DIR, "src", "protos"))  # Add protos directory to the path

TEST_GUILD = discord.Object(id=os.getenv("TEST_GUILD_ID")) if os.getenv("TEST_GUILD_ID") else None
IS_DEV_ENV = TEST_GUILD is not None

DEV_COMMANDS = {
    Movie,
}


def get_commands() -> list[Group | Command | ContextMenu]:
    """
    Get all the commands and context menus
    """

    package_names = ["commands", "context_menus"]

    commands = set()

    for package_name in package_names:
        for module_name in os.listdir(SRC_DIR / package_name):
            if module_name == "__init__.py" or not module_name.endswith(".py"):
                continue

            module = import_module(".".join([package_name, module_name.removesuffix(".py")]))

            # Get the command function from the module named same as the file name
            command = getattr(module, module_name.removesuffix(".py"), None)

            if command is not None:
                commands.add(command)

    for group_command_class in app_commands.Group.__subclasses__():
        if group_command_class in DEV_COMMANDS and not IS_DEV_ENV:
            continue

        commands.add(group_command_class())

    return list(commands)
