"""
Implements dice commands
"""

import os
from random import choice

import discord
from discord import app_commands
from discord.app_commands import Range

from utils import defer_response
from utils.templates import error
from utils.translator import Localization, DEFAULT_LANGUAGE

resources = [os.path.join("commands", "dice.ftl")]
default_loc = Localization(DEFAULT_LANGUAGE, resources)


MIN_VALUE = 1
MAX_VALUE = 6


@app_commands.command(name=default_loc.format_value("dice-name"),
                      description=default_loc.format_value("dice-description"))
@app_commands.describe(min_value=default_loc.format_value("dice-min-value-description",
                                                          {"default": MIN_VALUE}))
@app_commands.describe(max_value=default_loc.format_value("dice-max-value-description",
                                                          {"default": MAX_VALUE}))
async def dice(interaction: discord.Interaction,
               min_value: Range[int, 1] = MIN_VALUE,
               max_value: Range[int, 1] = MAX_VALUE):
    """Roll some dice"""

    send = await defer_response(interaction)

    loc = Localization(interaction.locale, resources)

    if min_value > max_value:
        await send(error(await loc.format_value_or_translate("dice-invalid-min-max-value")))
        return

    await send(await loc.format_value_or_translate("dice-rolled",
                                                   {"name": interaction.user.display_name,
                                                    "value": choice(range(min_value, max_value + 1))}), silent=True)

dice.extras["dice-min-value-description-default"] = MIN_VALUE
dice.extras["dice-max-value-description-default"] = MAX_VALUE
