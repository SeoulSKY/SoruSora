"""
Provides list of ui elements

classes:
    Confirm
    LanguageSelect
"""
import os

import discord
from discord import SelectOption, Interaction, Locale

from utils.templates import info, success
from utils.translator import languages, Localization, locale_to_code, get_resource


class Confirm(discord.ui.View):
    """
    Buttons for confirmation
    """

    def __init__(self, confirmed_message: str, cancelled_message: str, locale: Locale):
        """
        View to get a confirmation from a user. When the confirm button is pressed, set the is_confirmed to `True` and
        stop the View from listening to more input
        :param confirmed_message: A message to send when the user confirmed
        :param cancelled_message: A message to send when the user cancelled
        """
        super().__init__()

        self._loc = Localization(locale_to_code(locale), [os.path.join("utils", "ui.ftl")])

        self._confirmed_message = success(confirmed_message)
        self._cancelled_message = info(cancelled_message)

        self.confirm.label = self._loc.format_value("confirm")
        self.cancel.label = self._loc.format_value("cancel")

        self.is_confirmed = None
        """
        None: The user didn't respond\n
        True: The user confirmed\n
        False: The user cancelled
        """

    @discord.ui.button(style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, _: discord.ui.Button):
        """
        Confirm when pressed
        """
        self.is_confirmed = True
        await interaction.response.send_message(self._confirmed_message, ephemeral=True)
        self.stop()
        self.clear_items()

    @discord.ui.button(style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        """
        Cancel when pressed
        """
        self.is_confirmed = False
        await interaction.response.send_message(self._cancelled_message, ephemeral=True)
        self.stop()
        self.clear_items()


class LanguageSelect(discord.ui.Select):
    """
    Select UI to select available languages for a user
    """

    def __init__(self, placeholder: str, locale: Locale, min_values: int = 1, max_values: int = None):
        loc = Localization(locale_to_code(locale), [get_resource()])

        options = [SelectOption(label=loc.format_value(code), value=code) for code in languages]

        super().__init__(placeholder=placeholder, min_values=min_values,
                         max_values=max_values if max_values is not None else len(languages), options=options)

    async def callback(self, interaction: Interaction):
        raise NotImplementedError("This method should be overridden in a subclass")
