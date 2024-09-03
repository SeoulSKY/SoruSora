"""
This file contains the dashboard command.
"""

import os

from discord import Interaction, Embed, ChannelType
from discord.ui import View, ChannelSelect

from commands import command
from mongo.channel import get_channel
from mongo.chat import get_chat
from mongo.user import get_user
from utils import Localization, defer_response
from utils.constants import Limit, BOT_NAME
from utils.templates import color
from utils.translator import DEFAULT_LANGUAGE

resources = [os.path.join("commands", "dashboard.ftl")]

default_loc = Localization(DEFAULT_LANGUAGE, resources)


@command()
async def dashboard(interaction: Interaction):
    """
    Display the dashboard that contains the current configurations and statistics
    """

    send = await defer_response(interaction)
    loc = Localization(interaction.locale, resources)

    user = await get_user(interaction.user.id)
    chat = await get_chat(interaction.user.id)

    languages = [f"`{await loc.format_value_or_translate(code)}`" for code in user.translate_to]
    languages.sort()

    channels = [f"<#{channel_id}>" for channel_id in user.translate_in]

    user_embed = (Embed(color=color)
                  .add_field(
                                name=await loc.format_value_or_translate("translation-languages"),
                                value=", ".join(languages) or await loc.format_value_or_translate("none"),
                                inline=False
                            )
                  .add_field(
                                name=await loc.format_value_or_translate("translation-channels"),
                                value=", ".join(channels) or await loc.format_value_or_translate("none"),
                                inline=False
                            )
                  .add_field(
                                name=await loc.format_value_or_translate("history-length",
                                                                         {"name": BOT_NAME}),
                                value=len(chat.history) // 2,
                                inline=False
                            )
                  .set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url))

    if not (interaction.user.guild_permissions.manage_channels and interaction.user.guild_permissions.manage_threads):
        await send(embed=user_embed, ephemeral=True)
        return

    channel_select = ChannelSelect(
        placeholder=await loc.format_value_or_translate("select-channels"),
        channel_types=[x for x in ChannelType if x != ChannelType.category],
        max_values=Limit.NUM_EMBEDS_IN_MESSAGE.value
    )

    async def callback(select_interaction: Interaction):
        embeds = []
        for channel in channel_select.values:
            config = await get_channel(channel.id)

            languages = [f"`{await loc.format_value_or_translate(code)}`" for code in config.translate_to]
            languages.sort()

            main_language = await loc.format_value_or_translate("none")\
                if config.locale is None else f"`{await loc.format_value_or_translate(config.locale)}`"

            embed = (Embed(color=color, description=f"<#{channel.id}>")
                     .add_field(
                                    name=await loc.format_value_or_translate("translation-languages"),
                                    value=", ".join(languages) or await loc.format_value_or_translate("none"),
                                    inline=False
                                )
                     .add_field(
                                    name=await loc.format_value_or_translate("main-language"),
                                    value=main_language,
                                    inline=False
                                ))

            embeds.append(embed)

        await select_interaction.response.send_message(embeds=embeds, ephemeral=True)

    channel_select.callback = callback

    await send(embed=user_embed, view=View().add_item(channel_select), ephemeral=True)
