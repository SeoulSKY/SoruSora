"""
This module implements translator commands
"""
import asyncio
import os
from typing import Iterator

import langid
from discord import app_commands, Interaction, Message, Embed, HTTPException, Locale, ChannelType
from discord.ext.commands import Bot
from discord.ui import ChannelSelect

from mongo.channel import get_channel, set_channel
from mongo.user import get_user, set_user
from utils import defer_response, templates
from utils.constants import ErrorCode, Limit
from utils.templates import success
from utils.translator import Localization, Language, DEFAULT_LANGUAGE, get_translator, BaseTranslator
from utils.ui import LanguageSelectView

resources = [os.path.join("commands", "translator.ftl")]
default_loc = Localization(DEFAULT_LANGUAGE, resources)

ALL_CHANNELS_DEFAULT = True


class ChannelLanguageSelectView(LanguageSelectView):

    """
    Select UI to select available languages for a channel
    """

    def __init__(self, locale: Locale):
        self.loc = Localization(locale, resources)
        super().__init__(self.loc.format_value_or_translate("select-channel-languages"), locale)

    async def callback(self, interaction: Interaction):
        await super().callback(interaction)

        send = await defer_response(interaction)

        config = await get_channel(interaction.channel_id)
        config.translate_to = list(self.selected)
        await set_channel(config)

        await send(success(await self.loc.format_value_or_translate("channel-languages-updated")), ephemeral=True)


class UserLanguageSelectView(LanguageSelectView):
    # pylint: disable=too-few-public-methods
    """
    Select UI to select available languages for a user
    """

    def __init__(self, locale: Locale):
        self.loc = Localization(locale, resources)
        super().__init__(self.loc.format_value_or_translate("select-languages"), locale)

    async def callback(self, interaction: Interaction):
        await super().callback(interaction)

        send = await defer_response(interaction)

        config = await get_user(interaction.user.id)
        config.translate_to = list(self.selected)
        await set_user(config)

        await send(success(await self.loc.format_value_or_translate("languages-updated")), ephemeral=True)


class UserChannelSelect(ChannelSelect):
    """
    Select UI to select a channel for a user
    """

    def __init__(self, locale: Locale):
        self.loc = Localization(locale, resources)
        super().__init__(placeholder="Not initialized. Call init() first")

    async def init(self):
        """
        Initialize the channel select UI
        """
        super().__init__(placeholder=await self.loc.format_value_or_translate("select-channels"),
                         channel_types=[x for x in ChannelType if x != ChannelType.category],
                         max_values=int(Limit.SELECT_MAX))

        return self

    async def callback(self, interaction: Interaction):
        send = await defer_response(interaction)

        config = await get_user(interaction.user.id)
        config.translate_in = [channel.id for channel in self.values]
        await set_user(config)

        await send(success(await self.loc.format_value_or_translate("languages-updated")), ephemeral=True)


class Translator(app_commands.Group):
    """
    Commands related to translation
    """

    def __init__(self, bot: Bot):
        super().__init__(name=default_loc.format_value("translator-name"),
                         description=default_loc.format_value("translator-description"))
        self.bot = bot

        self._translator: BaseTranslator = get_translator()

        self._setup_user_listeners()
        self._setup_channel_listeners()

    def _setup_user_listeners(self):
        async def on_message(message: Message):
            usr = await get_user(message.author.id)
            if (
                    len(message.content.strip()) == 0 or
                    len(usr.translate_to) == 0 or
                    len(usr.translate_in) != 0 and message.channel.id not in usr.translate_in
            ):
                return

            if len(usr.translate_to) == 0:
                return

            await self._send_translation(message, map(Language, usr.translate_to))

        self.bot.add_listener(on_message)

    def _setup_channel_listeners(self):
        async def on_message(message: Message):
            if message.author == self.bot.user:
                return

            chan = await get_channel(message.channel.id)
            if len(message.content.strip()) == 0 or len(chan.translate_to) == 0:
                return

            if len(chan.translate_to) == 0:
                return

            await self._send_translation(message, map(Language, chan.translate_to))

        self.bot.add_listener(on_message)

    async def _send_translation(self, message: Message, dest_langs: Iterator[Language]) -> None:
        async with message.channel.typing():
            text = message.content
            source = Language((await asyncio.to_thread(langid.classify, text))[0])

            if len(message.embeds) != 0:
                text += "\n\n"
                for embed in message.embeds:
                    if embed.description is not None:
                        text += embed.description + "\n\n"

                text = text.removesuffix("\n\n")

            description = ""
            async for translation in self._translator.translate_targets(text, dest_langs, source):
                description += f"**__{translation.target.name}__**\n{translation.text}\n\n"

            description.removesuffix("\n\n")

            if len(description) == 0:
                return

            embeds = []
            for chunk in Translator._split(description, int(Limit.EMBED_DESCRIPTION_LEN)):
                embed = Embed(color=templates.color, description=chunk)
                embed.set_footer(text=message.author.display_name, icon_url=message.author.display_avatar.url)
                embeds.append(embed)

            try:
                await message.reply(embeds=embeds[0: min(len(embeds), int(Limit.NUM_EMBEDS_IN_MESSAGE))],
                                    silent=True)
            except HTTPException as ex:
                if ex.code == ErrorCode.MESSAGE_TOO_LONG:
                    await message.reply(templates.error("Cannot send the translated text because it is too long"),
                                        silent=True)
                    return

                raise ex

    @staticmethod
    def _split(string: str, count: int):
        for i in range(0, len(string), count):
            yield string[i: i + count]

    @app_commands.command(name=default_loc.format_value("set-languages-name"),
                          description=default_loc.format_value("set-languages-description"))
    @app_commands.describe(all_channels=default_loc.format_value(
        "set-languages-all-channels-description",
        {"set-languages-all-channels-description-default": str(ALL_CHANNELS_DEFAULT)})
    )
    async def set_languages(self, interaction: Interaction, all_channels: bool = ALL_CHANNELS_DEFAULT):
        """
        Set languages to be translated for your messages
        """

        send = await defer_response(interaction)

        view = await UserLanguageSelectView(interaction.locale).init()
        if all_channels:
            user = await get_user(interaction.user.id)
            user.translate_in = []
            await set_user(user)
        else:
            view.add_item(await UserChannelSelect(interaction.locale).init())

        await send(view=view, ephemeral=True)

    @app_commands.command(name=default_loc.format_value("set-channel-languages-name"),
                          description=default_loc.format_value("set-channel-languages-description"))
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel_languages(self, interaction: Interaction):
        """
        Set languages to be translated for this channel
        """

        send = await defer_response(interaction)

        await send(view=await ChannelLanguageSelectView(interaction.locale).init(), ephemeral=True)

    @app_commands.command(name=default_loc.format_value("clear-languages-name"),
                          description=default_loc.format_value("clear-languages-description"))
    async def clear_languages(self, interaction: Interaction):
        """
        Clear languages to be translated for your messages
        """

        send = await defer_response(interaction)

        user = await get_user(interaction.user.id)
        user.translate_to = []
        user.translate_in = []
        await set_user(user)

        loc = Localization(interaction.locale, resources)

        await send(success(await loc.format_value_or_translate("languages-cleared")), ephemeral=True)

    @app_commands.command(name=default_loc.format_value("clear-channel-languages-name"),
                          description=default_loc.format_value("clear-channel-languages-description"))
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_channel_languages(self, interaction: Interaction):
        """
        Clear languages to be translated for this channel
        """

        send = await defer_response(interaction)

        channel = await get_channel(interaction.channel_id)
        channel.translate_to = []
        await set_channel(channel)

        loc = Localization(interaction.locale, resources)

        await send(success(await loc.format_value_or_translate("channel-languages-cleared")), ephemeral=True)

    set_languages.extras["set-languages-all-channels-description-default"] = str(ALL_CHANNELS_DEFAULT)
