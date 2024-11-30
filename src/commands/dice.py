"""Implements dice commands."""

from pathlib import Path
from random import choice

import discord

from commands import command
from utils.translator import DEFAULT_LANGUAGE, Localization

resources = [Path("commands") / "dice.ftl"]
default_loc = Localization(DEFAULT_LANGUAGE, resources)


@command()
async def dice(interaction: discord.Interaction) -> None:
    """Roll some dice."""
    await interaction.response.send_message(
        choice([":one:", ":two:", ":three:", ":four:", ":five:", ":six:"]), silent=True  # noqa: S311
    )
