"""
Provides discord UIs that can be used for command

Classes:
    Confirm
"""

import discord

from utils.templates import success, info


class Confirm(discord.ui.View):
    """
    Buttons for confirmation
    """

    def __init__(self, *, confirmed_message: str = "Confirmed", cancelled_message: str = "Cancelled"):
        """
        View to get a confirmation from a user. When the confirm button is pressed, set the is_confirmed to `True` and
        stop the View from listening to more input
        :param confirmed_message: A message to send when the user confirmed
        :param cancelled_message: A message to send when the user cancelled
        """
        super().__init__()

        self._confirmed_message = success(confirmed_message)
        self._cancelled_message = info(cancelled_message)

        self.is_confirmed = None
        """
        None: The user didn't respond\n
        True: The user confirmed\n
        False: The user cancelled
        """

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, _: discord.ui.Button):
        """
        Confirm when pressed
        """
        self.is_confirmed = True
        await interaction.response.send_message(self._confirmed_message, ephemeral=True)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        """
        Cancel when pressed
        """
        self.is_confirmed = False
        await interaction.response.send_message(self._cancelled_message, ephemeral=True)
        self.stop()
