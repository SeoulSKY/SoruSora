"""
Implements ping commands
"""
import os

import discord
from discord import app_commands

from utils.constants import BOT_NAME
from utils.templates import info
from utils.translator import Localization

loc = Localization(["en"], [os.path.join("commands", "ping.ftl")])


@app_commands.command(name=loc.format_value("name"),
                      description=loc.format_value("description", {"name": BOT_NAME}))
async def ping(interaction: discord.Interaction):
    """Ping this bot"""
    await interaction.response.send_message(
        info(loc.format_value("latency", {"value": round(interaction.client.latency * 1000)})),
        ephemeral=True
    )
