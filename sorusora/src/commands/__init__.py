"""
This module contains the decorators that are used in the commands

Functions:
    update_locale
"""
import os
from typing import Callable, Coroutine

from discord import app_commands, Interaction

from mongo.user import get_user, set_user
from utils import Localization
from utils.constants import LOCALES_DIR
from utils.translator import DEFAULT_LANGUAGE


def update_locale():
    """
    A decorator to update the locale of the user
    """

    async def predicate(interaction: Interaction):
        user = await get_user(interaction.user.id)
        user.locale = str(interaction.locale)
        await set_user(user)
        return True

    return app_commands.check(predicate)


def command(*, nsfw: bool = False, **params: str):
    """
    A decorator to create a command

    :param nsfw: Whether the command is NSFW
    :param params: The parameters for the localization
    """

    args = {}
    for key, value in params.items():
        args[key.replace("_", "-")] = value

    loc = Localization(DEFAULT_LANGUAGE, [
        os.path.join("commands", name) for name in os.listdir(LOCALES_DIR / DEFAULT_LANGUAGE.code / "commands")
    ])

    def decorator(func: Callable[..., Coroutine]):
        return update_locale()(app_commands.command(
            name=loc.format_value(f"{func.__name__.strip('_').replace('_', '-')}-name", args),
            description=loc.format_value(f"{func.__name__.strip('_').replace('_', '-')}-description", args),
            nsfw=nsfw,
            extras=args
        ))(func)

    return decorator
