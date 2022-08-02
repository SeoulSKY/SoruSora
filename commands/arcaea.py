import discord
from discord import ui, app_commands, Interaction

import templates
from commands import Confirm
from main import ROOT_DIR


EMPTY_TEXT = "Empty"


class LinkPlayView(ui.View):
    @ui.button(label="Join", style=discord.ButtonStyle.primary)
    async def join(self, interaction: Interaction, button: ui.Button):
        embed = interaction.message.embeds[0]
        user = interaction.user

        if self._is_joined(embed, user):
            await interaction.response.send_message("You've already joined the Link Play", ephemeral=True)
            return

        if self._is_full(embed):
            await interaction.response.send_message("There are no more slots available", ephemeral=True)
            return

        for i in range(0, len(embed.fields)):
            if embed.fields[i].value == EMPTY_TEXT:
                embed.set_field_at(index=i, name=embed.fields[i].name, value=user.display_name)
                await interaction.message.edit(embed=embed)

                await interaction.response.send_message("Joined!", ephemeral=True)
                return

    def _is_joined(self, embed: discord.Embed, user: discord.User) -> bool:
        for field in embed.fields:
            if field.value == user.display_name:
                return True

        return False

    def _is_full(self, embed: discord.Embed) -> bool:
        for field in embed.fields:
            if field.value == EMPTY_TEXT:
                return False

        return True

    @ui.button(label="Leave")
    async def leave(self, interaction: Interaction, button: ui.Button):
        embed = interaction.message.embeds[0]
        user = interaction.user

        if not self._is_joined(embed, user):
            await interaction.response.send_message("You haven't joined the Link Play", ephemeral=True)
            return

        for i in range(0, len(embed.fields)):
            if embed.fields[i].value != user.display_name:
                continue

            if user.display_name == embed.author.name:
                confirm_view = Confirm(confirmed_message="Deleted")
                await interaction.response.send_message("You're about to delete the Link Play you created. Do you "
                                                        "want to continue?", view=confirm_view, ephemeral=True)
                await confirm_view.wait()

                if confirm_view.is_confirmed:
                    await interaction.message.delete()
            else:
                embed.set_field_at(index=i, name=embed.fields[i].name, value=EMPTY_TEXT)
                await interaction.message.edit(embed=embed)
                await interaction.response.send_message("You've left the Link Play", ephemeral=True)

            return


class Arcaea(app_commands.Group):
    """
    Commands related to Arcaea
    """

    @app_commands.command()
    async def linkplay(self, interaction: Interaction, roomcode: str):
        user = interaction.user

        embed = discord.Embed(color=templates.color,
                              title="Arcaea Link Play",
                              description=f"**{user.display_name}** is waiting for players to join")

        embed.add_field(name="Lead", value=user.display_name)

        num_players = 3
        for i in range(0, num_players):
            embed.add_field(name="Player", value=EMPTY_TEXT)

        embed.set_author(name=user.display_name, icon_url=user.avatar.url)
        embed.set_footer(text=f"Room code: {roomcode}")

        file = discord.File(f"{ROOT_DIR}/assets/link_play.png", filename="link_play.png")
        embed.set_thumbnail(url="attachment://link_play.png")

        await interaction.response.send_message(file=file, embed=embed, view=LinkPlayView())
