"""
This module implements arcaea command
"""

import datetime
import logging

import discord
from discord import ui, app_commands, Interaction, Forbidden
from discord.ext.commands import Bot

import templates
from commands import Confirm

EMPTY_TEXT = "Empty"

LINK_PLAY_LIFESPAN = datetime.timedelta(minutes=30)

logger = logging.getLogger(__name__)


class LinkPlayView(ui.View):
    """
    Buttons for LinkPlay message
    """

    def __init__(self):
        super().__init__(timeout=False)

    async def on_timeout(self) -> None:
        raise RuntimeError("Buttons are timed out and their interactions will fail")

    @ui.button(label="Join", custom_id="linkview-join-button", style=discord.ButtonStyle.primary)
    async def join(self, interaction: Interaction, _: ui.Button):
        """
        Add the username to the embed when pressed
        """
        embed = interaction.message.embeds[0]
        user = interaction.user

        if self._is_joined(embed, user):
            await interaction.response.send_message(templates.error("You've already joined the Link Play"),
                                                    ephemeral=True)
            return

        if self._is_full(embed):
            await interaction.response.send_message(templates.error("There are no more slots available"),
                                                    ephemeral=True)
            return

        await self._alert_others(interaction.guild, embed, user,
                                 templates.info(f"{user.mention} has joined the Link Play!"))

        for i, _ in enumerate(embed.fields):
            if embed.fields[i].value == EMPTY_TEXT:
                embed.set_field_at(index=i, name=embed.fields[i].name, value=user.mention)
                await interaction.message.edit(embed=embed)

                await interaction.response.send_message(templates.success("Joined!"), ephemeral=True)
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
            if field.value in (EMPTY_TEXT, interacted_user.mention):
                continue

            user = guild.get_member(int(field.value.removeprefix("<@").removesuffix(">")))
            try:
                await user.send(message)
            except Forbidden:
                pass

    @ui.button(label="Leave", custom_id="linkview-leave-button")
    async def leave(self, interaction: Interaction, _: ui.Button):
        """
        Remove the username from the embed when pressed
        """
        embed = interaction.message.embeds[0]
        user = interaction.user

        if not self._is_joined(embed, user):
            await interaction.response.send_message(templates.error("You haven't joined the Link Play"), ephemeral=True)
            return

        for i, _ in enumerate(embed.fields):
            if embed.fields[i].value != user.mention:
                continue

            lead_user_mention = embed.fields[0].value
            if user.mention == lead_user_mention:
                confirm_view = Confirm(confirmed_message="Deleted")
                await interaction.response.send_message(
                    templates.warning("You're about to delete the Link Play you created. Do you want to continue?"),
                    view=confirm_view, ephemeral=True)
                await confirm_view.wait()

                if confirm_view.is_confirmed:
                    await interaction.message.delete()
            else:
                await self._alert_others(interaction.guild, embed, user,
                                         templates.info(f"{user.mention} has left the Link Play"))

                embed.set_field_at(index=i, name=embed.fields[i].name, value=EMPTY_TEXT)
                await interaction.edit_original_response(embed=embed)
                await interaction.response.send_message(templates.success("You've left the Link Play"), ephemeral=True)

            return


class Arcaea(app_commands.Group):
    """
    Commands related to Arcaea
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(roomcode="Room code of your Arcaea Link Play")
    async def linkplay(self, interaction: Interaction, roomcode: str):
        """
        Create an embed to invite people to your Link Play. It will last for 30 minutes
        """

        user = interaction.user

        embed = discord.Embed(color=templates.color,
                              title="Arcaea Link Play",
                              description=f"{user.mention} is waiting for players to join")

        embed.add_field(name="Lead", value=user.mention)

        num_players = 3
        for _ in range(0, num_players):
            embed.add_field(name="Player", value=EMPTY_TEXT)

        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.set_footer(text=f"Room code: {roomcode}")
        embed.set_thumbnail(url="https://user-images.githubusercontent.com/48105703/"
                                "183126824-ac8d7b05-a8f2-4a7e-997a-24aafa762e24.png")

        await interaction.response.send_message(embed=embed, view=LinkPlayView())
        message = await interaction.original_response()
        await message.delete(delay=LINK_PLAY_LIFESPAN.total_seconds())
