"""
Implements translate context menus
"""
import os

import discord
from discord import app_commands

from utils import translator
from utils.translator import Localization, locale_to_code

loc = Localization(["en"], [os.path.join("context_menus", "translate.ftl")])


@app_commands.context_menu(name=loc.format_value("name"))
async def translate(interaction: discord.Interaction, message: discord.Message):
    """Translate this message into your language"""
    await interaction.response.send_message(
        translator.translate(message.content, locale_to_code(interaction.locale)), ephemeral=True
    )
