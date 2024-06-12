"""
Implements ping commands
"""
import os

import discord
from discord import app_commands

from utils import defer_response
from utils.constants import BOT_NAME
from utils.templates import info
from utils.translator import Localization, DEFAULT_LANGUAGE, format_localization

resources = [os.path.join("commands", "ping.ftl")]
default_loc = Localization(DEFAULT_LANGUAGE, resources)


@format_localization(ping_description_name=BOT_NAME)
@app_commands.command(name=default_loc.format_value("ping-name"),
                      description=default_loc.format_value("ping-description", {"ping-description-name": BOT_NAME}))
async def ping(interaction: discord.Interaction):
    """Ping this bot"""

    send = await defer_response(interaction)

    loc = Localization(interaction.locale, resources)

    await send(info(await loc.format_value_or_translate("latency",
                                                        {"value": round(interaction.client.latency * 1000)})),
               ephemeral=True)