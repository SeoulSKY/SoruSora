"""
Main script where the program starts
"""

import itertools
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from logging.handlers import TimedRotatingFileHandler
from threading import Lock

import discord
from discord import app_commands, Interaction, Locale, AppCommandType
from discord.app_commands import AppCommandError, MissingPermissions
from discord.ext.commands import Bot
from dotenv import load_dotenv
from tqdm import tqdm

from commands.movie import Movie
from utils import translator
from utils.constants import Limit, DEFAULT_LOCALE
from utils.templates import forbidden
from utils.translator import locale_to_code, Localization, CommandTranslator, Translator, has_localization, Translations

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
        super().__init__(command_prefix=None, intents=discord.Intents.all())
        self._add_commands()

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

    def _localize_commands(self, locales: list[str]) -> Translations:
        # pylint: disable=too-many-locals

        localizations = {}
        lock = Lock()

        def translate(locale: str, text: str) -> None:
            translated = translator.translate(text, locale, DEFAULT_LOCALE)

            with lock:
                localizations[locale][text] = translated[:int(Limit.COMMAND_DESCRIPTION_LEN)]

        def localize(loc: Localization, msg_id: str, text: str, snake_case: bool) -> None:
            result = loc.format_value(msg_id)
            transformed = "".join(char for char in result if char.isalnum()).lower().replace(" ", "_") \
                if snake_case else result

            with lock:
                localizations[loc.locales[0]][text] = transformed[:int(Limit.COMMAND_DESCRIPTION_LEN)]

        with ThreadPoolExecutor() as executor:
            for locale in locales:
                for command in self.tree.walk_commands():
                    loc = Localization(locale, [os.path.join(
                        "commands", f"{command.root_parent.name if command.root_parent else command.name}.ftl"
                    )])

                    command_prefix = command.name.replace('_', '-')

                    executor.submit(localize, loc, f"{command_prefix}-name", command.name, True)
                    executor.submit(localize, loc, f"{command_prefix}-description", command.description, False)

                    if isinstance(command, app_commands.Group):
                        continue

                    for name, description, choices in [(param.name, param.description, param.choices)
                                                       for param in command.parameters]:
                        executor.submit(localize, loc, f"{command_prefix}-{name}-name", name, True)
                        executor.submit(localize, loc, f"{command_prefix}-{name}-description", description, False)

                        for choice in choices:
                            executor.submit(translate, locale, choice.name)

                for context_menu in itertools.chain(self.tree.walk_commands(type=AppCommandType.message),
                                                    self.tree.walk_commands(type=AppCommandType.user)):
                    loc = Localization(locale, [os.path.join(
                        "context_menus", f"{context_menu.name.lower().replace(' ', '_')}.ftl"
                    )])

                    executor.submit(localize, loc, f"{context_menu.name.lower().replace(' ', '-')}-name",
                                    context_menu.name, False)

            executor.shutdown(wait=True)

        return localizations

    def _translate_commands(self, locales) -> Translations:
        """
        Translate the commands to given locales
        """

        translations = {}
        lock = Lock()
        pbar = tqdm(total=0, desc="Translating commands", unit="locale")

        def translate_batch(locale: str, texts: list[str], snake_case: list[bool]) -> None:
            with lock:
                pbar.total += 1

            translated = Translator(DEFAULT_LOCALE, locale).translate_batch(texts)

            with lock:
                for i, text in enumerate(texts):
                    result = "".join(char for char in translated[i]
                                     if char.isalnum()).lower().replace(" ", "_"
                                                                        ) if snake_case[i] else translated[i]
                    translations[locale][text] = result[:int(Limit.COMMAND_DESCRIPTION_LEN)]

                pbar.update()
                pbar.set_description(f"Translated commands ({locale})")

        with ThreadPoolExecutor() as executor:
            for locale in locales:
                locale = locale_to_code(locale)
                translations[locale] = {}

                batch = []
                snake_cases = []
                for command in self.tree.walk_commands():
                    batch.append(command.name)
                    snake_cases.append(True)

                    batch.append(command.description)
                    snake_cases.append(False)

                    if isinstance(command, app_commands.Group):
                        continue

                    for param in command.parameters:
                        batch.append(param.name)
                        snake_cases.append(True)

                        batch.append(param.description)
                        snake_cases.append(False)

                        batch.extend(choice.name for choice in param.choices)
                        snake_cases.extend(itertools.repeat(False, len(param.choices)))

                for context_menu in itertools.chain(self.tree.walk_commands(type=AppCommandType.message),
                                                    self.tree.walk_commands(type=AppCommandType.user)):
                    batch.append(context_menu.name)
                    snake_cases.append(False)

                executor.submit(translate_batch, locale, batch, snake_cases)

            executor.shutdown(wait=True)

        return translations

    async def setup_hook(self):
        localized = []
        non_localized = []

        for locale in map(locale_to_code, Locale):
            if has_localization(locale):
                localized.append(locale)
            else:
                non_localized.append(locale)

        translations = self._translate_commands(non_localized)
        localizations = self._localize_commands(localized)

        # merge two dicts
        for locale, localization in localizations.items():
            translations[locale] = localization

        localizations.clear()

        await self.tree.set_translator(CommandTranslator(translations))

        if IS_DEV_ENV:
            self.tree.copy_global_to(guild=TEST_GUILD)
            synced_commands = [command.name for command in await self.tree.sync(guild=TEST_GUILD)]
            logging.info("Synced commands to the test guild: %s", str(synced_commands))
        else:
            synced_commands = [command.name for command in await self.tree.sync()]
            logging.info("Synced commands to all guilds: %s", str(synced_commands))

        translations.clear()


bot = SoruSora()


@bot.event
async def on_ready():
    """
    Executed when the bot becomes ready
    """
    logging.info("Running in %s environment", "development" if IS_DEV_ENV else "production")
    logging.info("Logged in as %s (ID: %d)", bot.user, bot.user.id)


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
