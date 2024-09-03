"""
Implements dice commands
"""

import os
from random import choice

import discord

from commands import command
from utils.translator import Localization, DEFAULT_LANGUAGE

resources = [os.path.join("commands", "dice.ftl")]
default_loc = Localization(DEFAULT_LANGUAGE, resources)

@command()
async def dice(interaction: discord.Interaction):
    """Roll some dice"""

    await interaction.response.send_message(
        choice([":one:", ":two:", ":three:", ":four:", ":five:", ":six:"]), silent=True
    )
