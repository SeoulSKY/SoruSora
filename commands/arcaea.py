"""
This module implements arcaea commands
"""

import datetime
import logging
import os

import discord
from discord import app_commands, Interaction, Forbidden
from discord.ext.commands import Bot

from utils import templates, ui
from utils.constants import DEFAULT_LOCALE
from utils.translator import Localization

LINK_PLAY_LIFESPAN_MINUTES = 30
LINK_PLAY_LIFESPAN = datetime.timedelta(minutes=LINK_PLAY_LIFESPAN_MINUTES)

logger = logging.getLogger(__name__)

loc = Localization(DEFAULT_LOCALE, [os.path.join("commands", "arcaea.ftl")])
EMPTY_TEXT = loc.format_value("empty")


class LinkPlayView(discord.ui.View):
    """
    Buttons for LinkPlay message
    """

    def __init__(self):
        super().__init__(timeout=LINK_PLAY_LIFESPAN.total_seconds())

    async def on_timeout(self) -> None:
        """
        Delete the message when the view times out
        """
        self.clear_items()

    @discord.ui.button(label=loc.format_value("join"), style=discord.ButtonStyle.primary)
    async def join(self, interaction: Interaction, _: discord.ui.Button):
        """
        Add the username to the embed when pressed
        """
        embed = interaction.message.embeds[0]
        user = interaction.user

        if self._is_joined(embed, user):
            await interaction.response.send_message(templates.error(loc.format_value("already-joined")), ephemeral=True)
            return

        if self._is_full(embed):
            await interaction.response.send_message(templates.error(loc.format_value("full")), ephemeral=True)
            return

        await self._alert_others(interaction.guild, embed, user,
                                 templates.info(loc.format_value("joined-alert", {"user": user.mention})))

        for i, _ in enumerate(embed.fields):
            if embed.fields[i].value == EMPTY_TEXT:
                embed.set_field_at(index=i, name=embed.fields[i].name, value=user.mention)
                await interaction.message.edit(embed=embed)

                await interaction.response.send_message(templates.success(loc.format_value("joined")), ephemeral=True)
                return

    @staticmethod
    def _is_joined(embed: discord.Embed, user: discord.User) -> bool:
        for field in embed.fields:
            if field.value == user.mention:
                return True

        return False

    @staticmethod
    def _is_full(embed: discord.Embed) -> bool:
        for field in embed.fields:
            if field.value == EMPTY_TEXT:
                return False

        return True

    @staticmethod
    async def _alert_others(guild: discord.Guild, embed: discord.Embed, interacted_user: discord.User,
                            message: str) -> None:

        for field in embed.fields:
            if field.value in {EMPTY_TEXT, interacted_user.mention}:
                continue

            user = guild.get_member(int(field.value.removeprefix("<@").removesuffix(">")))
            if user is None:
                continue

            try:
                await user.send(message)
            except Forbidden:
                pass

    @discord.ui.button(label=loc.format_value("leave"))
    async def leave(self, interaction: Interaction, _: discord.ui.Button):
        """
        Remove the username from the embed when pressed
        """
        embed = interaction.message.embeds[0]
        user = interaction.user

        if not self._is_joined(embed, user):
            await interaction.response.send_message(templates.error(loc.format_value("not-joined")), ephemeral=True)
            return

        for i, _ in enumerate(embed.fields):
            if embed.fields[i].value != user.mention:
                continue

            lead_user_mention = embed.fields[0].value
            if user.mention == lead_user_mention:
                confirm_view = ui.Confirm(loc.format_value("deleted"), loc.format_value("cancelled"),
                                          interaction.locale)
                await interaction.response.send_message(templates.warning(loc.format_value("delete-confirm")),
                                                        view=confirm_view, ephemeral=True)
                await confirm_view.wait()

                if confirm_view.is_confirmed:
                    await interaction.message.delete()
            else:
                await self._alert_others(interaction.guild, embed, user,
                                         templates.info(loc.format_value("left-alert", {
                                             "user": user.mention})))

                embed.set_field_at(index=i, name=embed.fields[i].name, value=EMPTY_TEXT)
                await interaction.edit_original_response(embed=embed)
                await interaction.response.send_message(templates.success(loc.format_value("left")), ephemeral=True)

            return


class Arcaea(app_commands.Group):
    """
    Commands related to Arcaea
    """

    def __init__(self, bot: Bot):
        super().__init__(name=loc.format_value("arcaea-name"), description=loc.format_value("arcaea-description"))
        self.bot = bot

    @app_commands.command(name=loc.format_value("linkplay-name"),
                          description=loc.format_value("linkplay-description", {
                              "duration": LINK_PLAY_LIFESPAN_MINUTES
                          }))
    @app_commands.describe(roomcode=loc.format_value("linkplay-roomcode-description"))
    async def linkplay(self, interaction: Interaction, roomcode: str):
        """
        Create an embed to invite people to your Link Play
        """

        user = interaction.user

        embed = discord.Embed(color=templates.color, title=loc.format_value("title"),
                              description=loc.format_value("embed-description", {"user": user.mention}))

        embed.add_field(name=loc.format_value("lead"), value=user.mention)

        num_players = 3
        for _ in range(0, num_players):
            embed.add_field(name=loc.format_value("player"), value=EMPTY_TEXT)

        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.set_footer(text=loc.format_value("embed-roomcode", {"roomcode": roomcode}))
        embed.set_thumbnail(url="https://user-images.githubusercontent.com/48105703/"
                                "183126824-ac8d7b05-a8f2-4a7e-997a-24aafa762e24.png")

        await interaction.response.send_message(embed=embed, view=LinkPlayView())
        message = await interaction.original_response()
        await message.delete(delay=LINK_PLAY_LIFESPAN.total_seconds())
