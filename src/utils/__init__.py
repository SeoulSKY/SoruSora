"""Contains utility functions."""
from collections.abc import Sequence
from typing import Any

from discord import AllowedMentions, Embed, File, Interaction
from discord.abc import MISSING
from discord.ui import View

from utils.translator import Localization


async def defer_response(interaction: Interaction):  # noqa: ANN201
    """Defer the response if the locale is not supported.

    :param interaction: The interaction to respond to
    :return: The send function from the interaction
    """
    if Localization.has(interaction.locale):
        send_func = interaction.response.send_message
    else:
        await interaction.response.defer()
        send_func = interaction.followup.send


    async def send(  # noqa: PLR0913
        content: Any | None = None,  # noqa: ANN401
        *,
        embed: Embed = MISSING,
        embeds: Sequence[Embed] = MISSING,
        file: File = MISSING,
        files: Sequence[File] = MISSING,
        view: View = MISSING,
        tts: bool = False,
        ephemeral: bool = False,
        allowed_mentions: AllowedMentions = MISSING,
        suppress_embeds: bool = False,
        silent: bool = False,
        delete_after: float | None = None,
    ) -> None:
        await send_func(content,
                        embed=embed,
                        embeds=embeds,
                        file=file,
                        files=files,
                        view=view,
                        tts=tts,
                        ephemeral=ephemeral,
                        allowed_mentions=allowed_mentions,
                        suppress_embeds=suppress_embeds,
                        silent=silent,
                        delete_after=delete_after,
                        )

    return send
