"""Implements ping commands."""

from pathlib import Path

import discord

from commands import command
from utils import defer_response
from utils.constants import BOT_NAME
from utils.templates import info
from utils.translator import DEFAULT_LANGUAGE, Localization

resources = [Path("commands") / "ping.ftl"]
default_loc = Localization(DEFAULT_LANGUAGE, resources)


@command(ping_description_name=BOT_NAME)
async def ping(interaction: discord.Interaction) -> None:
    """Ping this bot."""
    send = await defer_response(interaction)

    loc = Localization(interaction.locale, resources)

    await send(
        info(
            await loc.format_value_or_translate(
                "latency", {"value": round(interaction.client.latency * 1000)}
            )
        ),
        ephemeral=True,
    )
