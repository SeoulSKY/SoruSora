"""
This module contains the decorators that are used in the commands

Functions:
    update_locale
"""


from discord import app_commands, Interaction

from mongo.user import get_user, set_user


def update_locale():
    """
    A decorator to update the locale of the user who is using the command
    """

    async def predicate(interaction: Interaction):
        user = await get_user(interaction.user.id)
        user.locale = str(interaction.locale)
        await set_user(user)

        return True

    return app_commands.check(predicate)
