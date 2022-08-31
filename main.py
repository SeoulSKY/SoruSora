"""
Main script where the program starts
"""

import logging
import os
from importlib import import_module

import discord
from discord import app_commands, Interaction
from discord.app_commands import AppCommandError, MissingPermissions
from discord.ext.commands import Bot
from dotenv import load_dotenv

from templates import forbidden

load_dotenv()

IS_DEV_ENV = "PRODUCTION" not in os.environ

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

LOGS_DIR = ROOT_DIR + "/logs/"

TEST_GUILD = discord.Object(id=os.getenv("TEST_GUILD_ID"))


class MyBot(Bot):
    """
    Class to be used to run the Discord Bot
    """

    def __init__(self):
        super().__init__(command_prefix="s!", intents=discord.Intents.all())
        self._add_commands()

    def _add_commands(self):
        package_name = "commands"

        for module_name in os.listdir(package_name):
            if module_name == "__init__.py" or not module_name.endswith(".py"):
                continue

            module = import_module("." + module_name.removesuffix(".py"), package_name)

            command = getattr(module, module_name.removesuffix(".py"), None)
            if command is not None:
                self.tree.add_command(command)

        for group_command_class in app_commands.Group.__subclasses__():
            # noinspection PyArgumentList
            self.tree.add_command(group_command_class(bot=self))

    async def setup_hook(self):
        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync()
        await self.tree.sync(guild=TEST_GUILD)


bot = MyBot()


@bot.event
async def on_ready():
    """
    Executed when the bot becomes ready
    """
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.tree.error
async def on_app_command_error(interaction: Interaction, error: AppCommandError):
    """
    Executed when an exception is raised while running app commands
    """
    if isinstance(error, MissingPermissions):
        await interaction.response.send_message(forbidden(str(error)), ephemeral=True)
        return

    raise error


if __name__ == "__main__":
    if not os.path.exists(LOGS_DIR):
        os.mkdir(LOGS_DIR)

    error_handler = logging.FileHandler(LOGS_DIR + "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logging.getLogger().addHandler(error_handler)

    bot.run(os.getenv("BOT_TOKEN"), log_handler=logging.StreamHandler(), log_level=logging.INFO, root_logger=True)
