import os
from typing import Callable, Coroutine

from discord import app_commands

from commands import update_locale
from utils import Localization
from utils.constants import LOCALES_DIR
from utils.translator import DEFAULT_LANGUAGE


def context_menu(*, nsfw: bool = False, **param: str):
    """
    A decorator to create a context menu

    :param nsfw: Whether the context menu is NSFW
    :param params: The parameters for the localization
    """

    args = {}
    for key, value in param.items():
        args[key.replace("_", "-")] = value

    loc = Localization(DEFAULT_LANGUAGE, [
        os.path.join("context_menus", name)
        for name in os.listdir(LOCALES_DIR / DEFAULT_LANGUAGE.code / "context_menus")
    ])

    def decorator(func: Callable[..., Coroutine]):
        return update_locale()(app_commands.context_menu(
            name=loc.format_value(f"{func.__name__.strip('_').replace('_', '-')}-name", args),
            nsfw=nsfw,
            extras=args
        ))(func)

    return decorator
