"""Implements the help command for the bot."""

from pathlib import Path

import aiofiles
from discord import AppCommandType, Interaction, app_commands
from discord.ui import View

from commands import command
from commands.movie import Movie
from utils import defer_response
from utils.constants import BOT_NAME, HELP_DIR
from utils.translator import DEFAULT_LANGUAGE, Cache, Language, Localization
from utils.ui import CommandSelect

resources = [Path("commands") / "help.ftl"]
default_loc = Localization(DEFAULT_LANGUAGE, resources)

HIDDEN_COMMANDS = {
    Movie,
}


def get_help_dir(command_name: str, language: Language) -> Path:
    """Get the help directory for a command."""
    return Path(HELP_DIR).joinpath(*command_name.split(" "), f"{language.code}.md")


class HelpSelect(CommandSelect):
    """Select UI to select a command."""

    def __init__(self, interaction: Interaction) -> None:
        """Initialize the help select."""
        loc = Localization(interaction.locale, resources)
        super().__init__(
            interaction,
            HIDDEN_COMMANDS,
            loc.format_value_or_translate("select-command"),
        )

    async def callback(self, interaction: Interaction) -> None:
        """Execute when a command is selected."""
        async with aiofiles.open(
            get_help_dir(self.values[0], DEFAULT_LANGUAGE), encoding="utf-8"
        ) as file:
            text = await file.read()

        translation = await Cache.get(Language(str(interaction.locale)), text)

        await interaction.response.send_message(translation.text, ephemeral=True)


@command(help_description_name=BOT_NAME, help_header_name=BOT_NAME)
async def help_(interaction: Interaction) -> None:
    """Show the help message."""
    from main import bot  # noqa: PLC0415

    send = await defer_response(interaction)

    loc = Localization(interaction.locale, resources)

    command_name = (
        interaction.command.name
        if loc.language == DEFAULT_LANGUAGE
        else await interaction.translate(interaction.command.name)
    )

    text = f"# /{command_name}\n"
    text += (
        await loc.format_value_or_translate(
            "help-header", {"help-header-name": BOT_NAME}
        )
        + "\n"
    )
    text += f"## {await loc.format_value_or_translate('commands')}\n"

    for cmd in bot.tree.walk_commands():
        if (
            isinstance(cmd, app_commands.Group)
            or cmd.root_parent.__class__ in HIDDEN_COMMANDS
        ):
            continue

        if loc.language == DEFAULT_LANGUAGE:
            text += f"* `/{cmd.qualified_name}`: {cmd.description}\n"
        else:
            translated_name = cmd.qualified_name.split(" ")
            for i, name in enumerate(translated_name):
                translated_name[i] = await interaction.translate(name)

            text += (
                f"* `/{' '.join(translated_name)}`: "
                f"{await interaction.translate(cmd.description)}\n"
            )

    text += (
        f"## {await loc.format_value_or_translate('context-menus')}\n"
        f"{await loc.format_value_or_translate('context-menus-description')} "
    )

    if interaction.user.is_on_mobile():
        text += (
            await loc.format_value_or_translate("context-menus-description-mobile")
            + "\n"
        )
    else:
        text += (
            f"{await loc.format_value_or_translate('context-menus-description-pc')}\n"
        )

    for context_menu in bot.tree.walk_commands(type=AppCommandType.message):
        if loc.language == DEFAULT_LANGUAGE:
            text += f"* `{context_menu.name}`\n"
        else:
            text += f"* `{await interaction.translate(context_menu.name)}`\n"

    await send(
        text, view=View().add_item(await HelpSelect(interaction).init()), ephemeral=True
    )
