"""
Implements ping commands
"""
import os

import discord
from discord import app_commands

from utils.constants import BOT_NAME, DEFAULT_LOCALE
from utils.templates import info
from utils.translator import Localization, locale_to_code

resources = [os.path.join("commands", "ping.ftl")]
default_loc = Localization(DEFAULT_LOCALE, resources)


@app_commands.command(name=default_loc.format_value("ping-name"),
                      description=default_loc.format_value("ping-description", {"ping-description-name": BOT_NAME}))
async def ping(interaction: discord.Interaction):
    """Ping this bot"""
    loc = Localization(locale_to_code(interaction.locale), resources)

    await interaction.response.send_message(
        info(loc.format_value_or_translate("latency",
                                           {"value": round(interaction.client.latency * 1000)})), ephemeral=True)

ping.extras["ping-description-name"] = BOT_NAME
