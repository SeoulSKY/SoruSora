"""
Implements a context menu to translate messages
"""
import os

import discord
from discord import app_commands

from utils import translator
from utils.constants import DEFAULT_LOCALE
from utils.translator import Localization, locale_to_code

loc = Localization(DEFAULT_LOCALE, [os.path.join("context_menus", "translate_message.ftl")])


@app_commands.context_menu(name=loc.format_value("translate-message-name"))
async def translate_message(interaction: discord.Interaction, message: discord.Message):
    """Translate this message into your language"""
    await interaction.response.send_message(
        translator.translate(message.content, locale_to_code(interaction.locale)), ephemeral=True
    )
