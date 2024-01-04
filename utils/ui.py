"""
Provides list of ui elements

classes:
    Confirm
    LanguageSelect
"""

import discord
from discord import SelectOption, Interaction
from firestore import user

from utils import constants
from utils.templates import info, success


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

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, _: discord.ui.Button):
        """
        Confirm when pressed
        """
        self.is_confirmed = True
        await interaction.response.send_message(self._confirmed_message, ephemeral=True)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        """
        Cancel when pressed
        """
        self.is_confirmed = False
        await interaction.response.send_message(self._cancelled_message, ephemeral=True)
        self.stop()


class LanguageSelect(discord.ui.Select):
    """
    Select UI to select available languages for a user
    """

    def __init__(self, min_values: int = 0, max_values: int = None, placeholder: str = None):
        for lang in constants.languages:
            assert constants.translator.is_language_supported(lang), f"{lang} is not a supported language"

        languages = [SelectOption(label=lang) for lang in constants.languages]

        super().__init__(placeholder=("Select languages that will be translated to"
                                      if placeholder is None else placeholder),
                         min_values=min_values,
                         max_values=max_values if max_values is not None else len(languages),
                         options=languages)

    async def callback(self, interaction: Interaction):
        config = await user.get_user(interaction.user.id)
        config.translate_to = self.values
        await user.set_user(config)

        await interaction.response.send_message(success("Your languages to be translated have been updated"),
                                                ephemeral=True)
