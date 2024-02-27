"""
Main script where the program starts
"""
import logging
import os
from importlib import import_module
from logging.handlers import TimedRotatingFileHandler

import discord
from discord import app_commands, Interaction
from discord.app_commands import AppCommandError, MissingPermissions
from discord.ext.commands import Bot, MinimalHelpCommand
from dotenv import load_dotenv

from commands.movie import Movie
from utils.templates import forbidden
from utils.translator import Localization, CommandTranslator

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

LOGS_DIR = os.path.join(ROOT_DIR, "logs")
ERROR_DIR = os.path.join(LOGS_DIR, "error")
WARNING_DIR = os.path.join(LOGS_DIR, "warning")

TEST_GUILD = discord.Object(id=os.getenv("TEST_GUILD_ID")) if os.getenv("TEST_GUILD_ID") else None
IS_DEV_ENV = TEST_GUILD is not None

DEV_COMMANDS = {
    Movie,
}


class EmptyHelpCommand(MinimalHelpCommand):
    """
    Help command that does nothing
    """
    async def send_pages(self) -> None:
        pass


class LevelFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """
    Logger filter that filters only specific logging level
    """

    def __init__(self, level: int):
        super().__init__()
        self._level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self._level


class SoruSora(Bot):
    """
    Class to be used to run the Discord Bot
    """

    def __init__(self):
        super().__init__(command_prefix="s!", intents=discord.Intents.all())

        self.help_command = EmptyHelpCommand()
        self._add_commands()

        self.event(self.on_ready)

    def _add_commands(self):
        package_names = ["commands", "context_menus"]

        for package_name in package_names:
            for module_name in os.listdir(package_name):
                if module_name == "__init__.py" or not module_name.endswith(".py"):
                    continue

                module = import_module("." + module_name.removesuffix(".py"), package_name)

                command = getattr(module, module_name.removesuffix(".py"), None)
                if command is not None:
                    self.tree.add_command(command)

        for group_command_class in app_commands.Group.__subclasses__():
            if group_command_class in DEV_COMMANDS and not IS_DEV_ENV:
                continue

            # noinspection PyArgumentList
            self.tree.add_command(group_command_class(bot=self))

    async def setup_hook(self):
        await self.tree.set_translator(CommandTranslator(self))

        if IS_DEV_ENV:
            self.tree.copy_global_to(guild=TEST_GUILD)
            synced_commands = [command.name for command in await self.tree.sync(guild=TEST_GUILD)]
            logging.info("Synced commands to the test guild: %s", str(synced_commands))
        else:
            synced_commands = [command.name for command in await self.tree.sync()]
            logging.info("Synced commands to all guilds: %s", str(synced_commands))

    async def on_ready(self):
        """
        Executed when the bot becomes ready
        """

        logging.info("Running in %s environment", "development" if IS_DEV_ENV else "production")
        logging.info("Logged in as %s (ID: %d)", self.user, self.user.id)


bot = SoruSora()


@bot.tree.error
async def on_app_command_error(interaction: Interaction, error: AppCommandError):
    """
    Executed when an exception is raised while running app commands
    """

    if not isinstance(error, MissingPermissions):
        raise error

    loc = Localization(interaction.locale, ["main.ftl"])
    await interaction.response.send_message(
        forbidden(await loc.format_value_or_translate("missing-permission")),
        ephemeral=True
    )


if __name__ == "__main__":
    os.makedirs(ERROR_DIR, exist_ok=True)
    os.makedirs(WARNING_DIR, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    error_log_path = os.path.join(ERROR_DIR, "error")
    error_handler = TimedRotatingFileHandler(error_log_path, when="d", delay=True)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    warning_log_path = os.path.join(WARNING_DIR, "warning")
    warning_handler = TimedRotatingFileHandler(warning_log_path, when="d", delay=True)
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(error_handler)
    logger.addHandler(warning_handler)

    bot.run(os.getenv("BOT_TOKEN"), log_handler=logging.StreamHandler(), log_level=logging.INFO, root_logger=True)
