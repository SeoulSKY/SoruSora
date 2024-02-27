"""
Implements dice commands
"""

import os
from random import choice

import discord
from discord import app_commands
from utils.translator import Localization, DEFAULT_LANGUAGE

resources = [os.path.join("commands", "dice.ftl")]
default_loc = Localization(DEFAULT_LANGUAGE, resources)


@app_commands.command(name=default_loc.format_value("dice-name"),
                      description=default_loc.format_value("dice-description"))
async def dice(interaction: discord.Interaction):
    """Roll some dice"""

    await interaction.response.send_message(
        choice([":one:", ":two:", ":three:", ":four:", ":five:", ":six:"]), silent=True
    )
