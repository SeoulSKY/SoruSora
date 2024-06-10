"""
Implements the help command for the bot.
"""
import os

from discord import app_commands, Interaction, AppCommandType
from discord.ui import View

from commands.movie import Movie
from utils import defer_response
from utils.constants import BOT_NAME, HELP_DIR
from utils.translator import Cache
from utils.translator import Localization, Language, DEFAULT_LANGUAGE
from utils.ui import CommandSelect

resources = [os.path.join("commands", "help.ftl")]
default_loc = Localization(DEFAULT_LANGUAGE, resources)

HIDDEN_COMMANDS = {
    Movie,
}


def get_help_dir(command_name: str, language: Language) -> str:
    """
    Get the help directory for a command
    """
    return str(os.path.join(HELP_DIR, *command_name.split(" "), f"{language.code}.md"))


class HelpSelect(CommandSelect):
    """
    Select UI to select a command
    """
    def __init__(self, interaction: Interaction):
        loc = Localization(interaction.locale, resources)
        super().__init__(interaction, HIDDEN_COMMANDS, loc.format_value_or_translate("select-command"))

    async def callback(self, interaction: Interaction):
        """
        Callback for the command selection
        """

        with open(get_help_dir(self.values[0], DEFAULT_LANGUAGE), "r", encoding="utf-8") as file:
            text = file.read()

        await interaction.response.send_message(Cache.get(Language(str(interaction.locale)), text).text, ephemeral=True)


@app_commands.command(name=default_loc.format_value("help-name"),
                      description=default_loc.format_value("help-description",
                                                           {"help-description-name": BOT_NAME}))
async def help_(interaction: Interaction):
    """
    Show the help message
    """

    # pylint: disable=import-outside-toplevel
    from main import bot

    send = await defer_response(interaction)

    loc = Localization(interaction.locale, resources)

    command_name = (interaction.command.name
                    if loc.language == DEFAULT_LANGUAGE else await interaction.translate(interaction.command.name))

    text = f"# /{command_name}\n"
    text += await loc.format_value_or_translate("help-header", {"help-header-name": BOT_NAME}) + "\n"
    text += f"## {await loc.format_value_or_translate('commands')}\n"

    for command in bot.tree.walk_commands():
        if isinstance(command, app_commands.Group) or command.root_parent.__class__ in HIDDEN_COMMANDS:
            continue

        if loc.language == DEFAULT_LANGUAGE:
            text += f"* `/{command.qualified_name}`: {command.description}\n"
        else:
            translated_name = command.qualified_name.split(" ")
            for i, name in enumerate(translated_name):
                translated_name[i] = await interaction.translate(name)

            text += f"* `/{' '.join(translated_name)}`: {await interaction.translate(command.description)}\n"

    text += (f"## {await loc.format_value_or_translate('context-menus')}\n"
             f"{await loc.format_value_or_translate('context-menus-description')} ")

    if interaction.user.is_on_mobile():
        text += f"{await loc.format_value_or_translate('context-menus-description-mobile')}\n"
    else:
        text += f"{await loc.format_value_or_translate('context-menus-description-pc')}\n"

    for context_menu in bot.tree.walk_commands(type=AppCommandType.message):
        if loc.language == DEFAULT_LANGUAGE:
            text += f"* `{context_menu.name}`\n"
        else:
            text += f"* `{await interaction.translate(context_menu.name)}`\n"

    await send(text, view=View().add_item(await HelpSelect(interaction).init()), ephemeral=True)


help_.extras["help-description-name"] = BOT_NAME
help_.extras["help-header-name"] = BOT_NAME
