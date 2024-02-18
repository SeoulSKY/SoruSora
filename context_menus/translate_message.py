"""
Implements translate
"""

import discord
from discord import app_commands


@app_commands.context_menu(name="Translate Message")
async def translate_message(interaction: discord.Interaction, _: discord.Message):
    """Translate this message into your language"""
    await interaction.response.send_message("hello", ephemeral=True)
