"""Implements dice commands."""

from pathlib import Path
from typing import Self

import aiofiles
import discord
from discord import ButtonStyle, Interaction
from discord.ui import Button

from commands import command
from utils import defer_response
from utils.constants import ABOUT_DIR, BOT_NAME, BUG_REPORT_URL, GITHUB_URL, INVITE_URL
from utils.translator import DEFAULT_LANGUAGE, Cache, Language, Localization

resources = [Path("commands") / "about.ftl"]
default_loc = Localization(DEFAULT_LANGUAGE, resources)


def get_about_dir(language: Language) -> Path:
    """Get the 'about' directory for a language."""
    code = (
        language.code if Localization.has(language.code) else language.trim_territory()
    )
    return ABOUT_DIR / f"{code}.md"


class AboutView(discord.ui.View):
    """View for the about command."""

    def __init__(self, interaction: Interaction) -> None:
        """Initialize the about view."""
        super().__init__()

        self._interaction = interaction

    async def init(self) -> Self:
        """Initialize the view."""
        loc = Localization(Language(self._interaction.locale), resources)

        buttons = [
            Button(
                label=await loc.format_value_or_translate("invite"),
                style=ButtonStyle.link,
                url=INVITE_URL,
            ),
            Button(
                label=await loc.format_value_or_translate("github"),
                style=ButtonStyle.link,
                url=GITHUB_URL,
            ),
            Button(
                label=await loc.format_value_or_translate("bug-report"),
                style=ButtonStyle.link,
                url=BUG_REPORT_URL,
            ),
            Button(
                label=await loc.format_value_or_translate("contribute"),
                style=ButtonStyle.link,
                url="https://github.com/SeoulSKY/SoruSora/blob/master/docs/CONTRIBUTING.md",
            ),
            Button(
                label=await loc.format_value_or_translate("developer"),
                style=ButtonStyle.link,
                url="https://www.seoulsky.org",
            ),
            Button(
                label=await loc.format_value_or_translate("terms-of-service"),
                style=ButtonStyle.link,
                url="https://github.com/SeoulSKY/SoruSora/blob/main/TERMS_OF_SERVICE.md",
            ),
            Button(
                label=await loc.format_value_or_translate("privacy-policy"),
                style=ButtonStyle.link,
                url="https://github.com/SeoulSKY/SoruSora/blob/main/PRIVACY_POLICY.md",
            )
        ]

        for button in buttons:
            self.add_item(button)

        return self


@command(about_description_name=BOT_NAME)
async def about(interaction: Interaction) -> None:
    """Show information about the bot."""
    send = await defer_response(interaction)

    async with aiofiles.open(get_about_dir(DEFAULT_LANGUAGE), encoding="utf-8") as file:
        text = await file.read()

    translation = await Cache.get(Language(str(interaction.locale)), text)

    await send(
        translation.text,
        view=await AboutView(interaction).init(),
    )
