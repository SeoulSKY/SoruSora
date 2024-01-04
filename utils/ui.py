"""
Provides list of ui elements

classes:
    LanguageSelect
"""

import discord
from discord import SelectOption, Interaction
from firestore import user

from utils import constants
from utils.templates import success


class LanguageSelect(discord.ui.Select):
    """
    Select UI to select available languages for a user
    """

    def __init__(self, min_values: int = 0, max_values: int = None, placeholder: str = None):
        for lang in constants.languages:
            assert constants.translator.is_language_supported(lang), f"{lang} is not a supported language"

        languages = [SelectOption(label=lang) for lang in constants.languages]

        max_values_possible = 25
        super().__init__(placeholder=("Select languages that will be translated to"
                                      if placeholder is None else placeholder),
                         min_values=min_values,
                         max_values=max_values if max_values is not None else min(max_values_possible, len(languages)),
                         options=languages[: max_values_possible])

    async def callback(self, interaction: Interaction):
        config = await user.get_user(interaction.user.id)
        config.translate_to = self.values
        await user.set_user(config)

        await interaction.response.send_message(success("Your languages to be translated have been updated"),
                                                ephemeral=True)
