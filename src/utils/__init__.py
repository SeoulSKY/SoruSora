"""Contains utility functions."""
from collections.abc import Coroutine

from discord import Interaction

from utils.translator import Localization


async def defer_response(interaction: Interaction) -> Coroutine:
    """Defer the response if the locale is not supported.

    :param interaction: The interaction to respond to
    :return: The send function from the interaction
    """
    if Localization.has(interaction.locale):
        return interaction.response.send_message

    await interaction.response.defer()
    return interaction.followup.send
