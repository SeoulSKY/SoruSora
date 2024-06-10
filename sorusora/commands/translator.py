"""
This module implements translator commands
"""
import asyncio
import os
from typing import Iterable

import langid
from discord import app_commands, Interaction, Message, Embed, HTTPException, Locale
from discord.ext.commands import Bot

from mongo.channel import get_channel, set_channel
from mongo.user import get_user, set_user
from utils import defer_response, templates
from utils.constants import ErrorCode, Limit
from utils.templates import success
from utils.translator import Localization, Language, DEFAULT_LANGUAGE, get_translator, BaseTranslator
from utils.ui import LanguageSelectView, ChannelSelect, SubmitButton

resources = [os.path.join("commands", "translator.ftl")]
default_loc = Localization(DEFAULT_LANGUAGE, resources)

ALL_CHANNELS_DEFAULT = True
THIS_CHANNEL_DEFAULT = True


class TranslatorLanguageSelectView(LanguageSelectView):
    """
    Select UI to select available languages for a translator
    """

    def __init__(self, locale: Locale):
        """
        Create a view to select languages for a translator
        :param locale: The locale of the user
        """

        loc = Localization(locale, resources)
        super().__init__(loc.format_value_or_translate("select-languages"), locale)


class TranslatorChannelSelect(ChannelSelect):
    """
    Select UI to select channels for a translator
    """

    def __init__(self, locale: Locale):
        """
        Create a view to select channels for a translator
        :param locale: The locale of the user
        """

        loc = Localization(locale, resources)
        super().__init__(placeholder=loc.format_value_or_translate("select-channels"))


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

            languages = []
            for code in usr.translate_to:
                if self._translator.is_code_supported(code):
                    languages.append(Language(code))

            await self._send_translation(message, languages)

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

            languages = []
            for code in chan.translate_to:
                if self._translator.is_code_supported(code):
                    languages.append(Language(code))

            await self._send_translation(message, languages)

        self.bot.add_listener(on_message)

    async def _send_translation(self, message: Message, dest_langs: Iterable[Language]) -> None:
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
                if translation.source == translation.target:
                    continue

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

        loc = Localization(interaction.locale, resources)
        send = await defer_response(interaction)

        language_view = await TranslatorLanguageSelectView(interaction.locale).init()
        channel_select = await TranslatorChannelSelect(interaction.locale).init()

        async def on_submit(interaction: Interaction):
            config = await get_user(interaction.user.id)
            config.translate_to = list(language_view.selected)
            config.translate_in = [] if all_channels else [channel.id for channel in channel_select.values]
            await set_user(config)

            await interaction.response.send_message(
                success(await loc.format_value_or_translate("languages-updated")),
                ephemeral=True
            )

        button = await SubmitButton(interaction.locale).init()
        button.callback = on_submit

        if not all_channels:
            language_view.add_item(channel_select)

        language_view.add_item(button)

        await send(view=language_view, ephemeral=True)

    @app_commands.command(name=default_loc.format_value("set-channel-languages-name"),
                          description=default_loc.format_value("set-channel-languages-description"))
    @app_commands.describe(this_channel=default_loc.format_value(
        "set-channel-languages-this-channel-description",
        {"set-channel-languages-this-channel-description-default": str(THIS_CHANNEL_DEFAULT)})
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel_languages(self, interaction: Interaction, this_channel: bool = THIS_CHANNEL_DEFAULT):
        """
        Set languages to be translated for channels
        """

        loc = Localization(interaction.locale, resources)
        send = await defer_response(interaction)

        language_view = await TranslatorLanguageSelectView(interaction.locale).init()
        channel_select = await TranslatorChannelSelect(interaction.locale).init()

        async def on_submit(interaction: Interaction):
            channels = [interaction.channel_id] if this_channel else [channel.id for channel in channel_select.values]
            for channel in channels:
                config = await get_channel(channel)
                config.translate_to = list(language_view.selected)
                await set_channel(config)

            await interaction.response.send_message(
                success(await loc.format_value_or_translate("languages-updated")),
                ephemeral=True
            )

        button = await SubmitButton(interaction.locale).init()
        button.callback = on_submit

        if not this_channel:
            language_view.add_item(channel_select)

        language_view.add_item(button)

        await send(view=language_view, ephemeral=True)

    set_languages.extras["set-languages-all-channels-description-default"] = str(ALL_CHANNELS_DEFAULT)
    set_channel_languages.extras["set-channel-languages-this-channel-description-default"] = str(THIS_CHANNEL_DEFAULT)
