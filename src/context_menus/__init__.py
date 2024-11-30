"""Implements decorators for context menus."""

import os
from collections.abc import Callable, Coroutine
from pathlib import Path

from discord import app_commands
from discord.app_commands import Command

from commands import update_locale
from utils import Localization
from utils.constants import LOCALES_DIR
from utils.translator import DEFAULT_LANGUAGE


def context_menu(*, nsfw: bool = False, **params: str) -> Callable[[...], Command]:
    """Decorate the context menu.

    :param nsfw: Whether the context menu is NSFW
    :param params: The parameters for the localization
    """
    args = {}
    for key, value in params.items():
        args[key.replace("_", "-")] = value

    loc = Localization(
        DEFAULT_LANGUAGE,
        [
            Path("context_menus") / name
            for name in os.listdir(
                LOCALES_DIR / DEFAULT_LANGUAGE.code / "context_menus"
            )
        ],
    )

    def decorator(func: Callable[..., Coroutine]) -> Command:
        return update_locale()(
            app_commands.context_menu(
                name=loc.format_value(
                    f"{func.__name__.strip('_').replace('_', '-')}-name", args
                ),
                nsfw=nsfw,
                extras=args,
            )
        )(func)

    return decorator
