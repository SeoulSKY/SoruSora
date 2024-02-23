"""
Implements the help command for the bot.
"""
import os

from discord import app_commands, Interaction, AppCommandType
from discord.ui import View

from commands.movie import Movie
from main import bot
from utils.constants import DEFAULT_LOCALE, BOT_NAME, HELP_DIR
from utils.translator import Localization, locale_to_code, has_localization, is_english, translate
from utils.ui import CommandSelect

resources = [os.path.join("commands", "help.ftl")]
default_loc = Localization(DEFAULT_LOCALE, resources)

HIDDEN_COMMANDS = {
    Movie,
}


class HelpSelect(CommandSelect):
    """
    Select UI to select a command
    """
    def __init__(self, interaction: Interaction):
        loc = Localization(interaction.locale, resources)
        super().__init__(interaction, HIDDEN_COMMANDS, placeholder=loc.format_value_or_translate("select-command"))

    async def callback(self, interaction: Interaction):
        command_name = self.values[0]
        locale = locale_to_code(interaction.locale)

        if has_localization(locale):
            path = os.path.join(HELP_DIR, *command_name.split(" "), f"{locale}.md")
        else:
            path = os.path.join(HELP_DIR, *command_name.split(" "), f"{DEFAULT_LOCALE}.md")

        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
            if not has_localization(locale):
                text = translate(text, locale, DEFAULT_LOCALE)

        await interaction.response.send_message(text, ephemeral=True)


@app_commands.command(name=default_loc.format_value("help-name"),
                      description=default_loc.format_value("help-description",
                                                           {"help-description-name": BOT_NAME}))
async def _help(interaction: Interaction):
    """
    Show the help message
    """

    loc = Localization(interaction.locale, resources)
    english = is_english(locale_to_code(interaction.locale))

    command_name = interaction.command.name if english else await interaction.translate(interaction.command.name)
    text = f"# /{command_name}\n## {loc.format_value_or_translate('commands')}\n"

    for command in bot.tree.walk_commands():
        if isinstance(command, app_commands.Group) or command.root_parent.__class__ in HIDDEN_COMMANDS:
            continue

        if english:
            text += f"* `/{command.qualified_name}`: {command.description}\n"
        else:
            translated_name = command.qualified_name.split(" ")
            for i, name in enumerate(translated_name):
                translated_name[i] = await interaction.translate(name)

            text += f"* `/{' '.join(translated_name)}`: {await interaction.translate(command.description)}\n"

    text += (f"## {loc.format_value_or_translate('context-menus')}\n"
             f"{loc.format_value_or_translate('context-menus-description')} ")

    if interaction.user.is_on_mobile():
        text += f"{loc.format_value_or_translate('context-menus-description-mobile')}\n"
    else:
        text += f"{loc.format_value_or_translate('context-menus-description-pc')}\n"

    for context_menu in bot.tree.walk_commands(type=AppCommandType.message):
        if english:
            text += f"* `{context_menu.name}`\n"
        else:
            text += f"* `{await interaction.translate(context_menu.name)}`\n"

    await interaction.response.send_message(text, view=View().add_item(HelpSelect(interaction)), ephemeral=True)


_help.extras["help-description-name"] = BOT_NAME
