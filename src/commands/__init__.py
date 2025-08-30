"""Contains the decorators that are used in the commands."""

from collections.abc import Callable, Coroutine
from pathlib import Path

from discord import Interaction, app_commands
from discord.app_commands import Command

from mongo.user import get_user, set_user
from utils import Localization
from utils.constants import LOCALES_DIR
from utils.translator import DEFAULT_LANGUAGE


def update_locale() -> Callable[..., Callable[[Coroutine], Command]]:
    """Decorate a function to update the locale of the user."""

    async def predicate(interaction: Interaction) -> bool:
        user = await get_user(interaction.user.id)
        user.locale = str(interaction.locale)
        await set_user(user)
        return True

    return app_commands.check(predicate)


def command(*, nsfw: bool = False, **params: str) -> [Callable[..., Command]]:
    """Decorate a function to create a command.

    :param nsfw: Whether the command is NSFW
    :param params: The parameters for the localization
    """
    args = {}
    for key, value in params.items():
        args[key.replace("_", "-")] = value

    loc = Localization(
        DEFAULT_LANGUAGE,
        [
            Path("commands") / path.name
            for path in (LOCALES_DIR / DEFAULT_LANGUAGE.code / "commands").iterdir()
        ],
    )

    def decorator(func: Coroutine) -> Command:
        return update_locale()(
            app_commands.command(
                name=loc.format_value(
                    f"{func.__name__.strip('_').replace('_', '-')}-name", args
                ),
                description=loc.format_value(
                    f"{func.__name__.strip('_').replace('_', '-')}-description", args
                ),
                nsfw=nsfw,
                extras=args,
            )
        )(func)

    return decorator
