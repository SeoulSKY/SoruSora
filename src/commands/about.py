"""
Implements dice commands
"""

import os

import discord
from discord import Interaction, ButtonStyle
from discord.ui import Button

from commands import command
from utils import defer_response
from utils.constants import BOT_NAME, ABOUT_DIR, BUG_REPORT_URL, GITHUB_URL, INVITE_URL
from utils.translator import Localization, DEFAULT_LANGUAGE, Language, Cache

resources = [os.path.join("commands", "about.ftl")]
default_loc = Localization(DEFAULT_LANGUAGE, resources)


def get_about_dir(language: Language) -> str:
    """
    Get the 'about' directory for a language
    """
    code = language.code if Localization.has(language.code) else language.trim_territory()
    return str(os.path.join(ABOUT_DIR, f"{code}.md"))


class AboutView(discord.ui.View):
    """
    View for the about command
    """

    def __init__(self, interaction: Interaction):
        super().__init__()

        self._interaction = interaction

    async def init(self):
        """
        Initialize the view
        """

        loc = Localization(Language(self._interaction.locale), resources)

        buttons = [
            Button(label=await loc.format_value_or_translate("invite"),
                   style=ButtonStyle.link,
                   url=INVITE_URL),
            Button(label=await loc.format_value_or_translate("github"),
                   style=ButtonStyle.link,
                   url=GITHUB_URL),
            Button(label=await loc.format_value_or_translate("bug-report"),
                   style=ButtonStyle.link,
                   url=BUG_REPORT_URL),
            Button(label=await loc.format_value_or_translate("contribute"),
                   style=ButtonStyle.link,
                   url="https://github.com/SeoulSKY/SoruSora/blob/master/docs/CONTRIBUTING.md"),
            Button(label=await loc.format_value_or_translate("developer"),
                   style=ButtonStyle.link,
                   url="https://www.seoulsky.org")
        ]

        for button in buttons:
            self.add_item(button)

        return self


@command(about_description_name=BOT_NAME)
async def about(interaction: Interaction):
    """Show information about the bot"""

    send = await defer_response(interaction)

    with open(get_about_dir(DEFAULT_LANGUAGE), "r", encoding="utf-8") as file:
        text = file.read()

    await send(Cache.get(Language(str(interaction.locale)), text).text, view=await AboutView(interaction).init())
