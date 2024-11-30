"""Implements a context menu to translate messages."""

from pathlib import Path

import discord

import utils.translator
from context_menus import context_menu
from utils import defer_response
from utils.templates import error
from utils.translator import DEFAULT_LANGUAGE, Language, Localization

resources = [Path("context_menus") / "translate_message.ftl"]
default_loc = Localization(DEFAULT_LANGUAGE, resources)


@context_menu()
async def translate_message(interaction: discord.Interaction,
                            message: discord.Message) -> None:
    """Translate this message into your language."""
    send = await defer_response(interaction)
    loc = Localization(interaction.locale, resources)

    translator = utils.translator.get_translator()
    language = Language(str(interaction.locale))

    if not translator.is_language_supported(language):
        await send(
            error(
                await loc.format_value_or_translate(
                    "language-not-supported", {"name": language.name}
                )
            ),
            ephemeral=True,
        )
        return

    await send(await translator.translate(message.content, language), ephemeral=True)
