"""
Implements a context menu to translate messages
"""
import os

import discord
from discord import app_commands

import utils.translator
from utils.templates import error
from utils.translator import Localization, DEFAULT_LANGUAGE, Language

loc = Localization(DEFAULT_LANGUAGE, [os.path.join("context_menus", "translate_message.ftl")])


@app_commands.context_menu(name=loc.format_value("translate-message-name"))
async def translate_message(interaction: discord.Interaction, message: discord.Message):
    """Translate this message into your language"""
    translator = utils.translator.get_translator()
    language = Language(str(interaction.locale))

    if not translator.is_language_supported(language):
        await interaction.response.send_message(
            error(await loc.format_value_or_translate("language-not-supported", {"name": language.name})),
            ephemeral=True
        )
        return


    await interaction.followup.send(translator.translate(message.content, language), ephemeral=True)
