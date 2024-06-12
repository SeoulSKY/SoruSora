"""
This module implements translator commands
"""
import asyncio
import os
from typing import Iterable

import langid
from discord import app_commands, Interaction, Message, Embed, HTTPException, Locale

from commands import localization_args, listener
from mongo.channel import get_channel, set_channel
from mongo.user import get_user, set_user
from utils import defer_response, templates
from utils.constants import ErrorCode, Limit
from utils.templates import success, error
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

    def __init__(self, interaction: Interaction, max_values: int = None):
        """
        Create a view to select languages for a translator
        :param interaction: The interaction of the command
        :param max_values: Maximum number of values that can be selected
        """

        loc = Localization(interaction.locale, resources)
        super().__init__(interaction, loc.format_value_or_translate("select-languages"), max_values)


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

    def __init__(self):
        super().__init__(name=default_loc.format_value("translator-name"),
                         description=default_loc.format_value("translator-description"))
        self._translator: BaseTranslator = get_translator()

        @listener
        async def on_message(message: Message):
            """
            Executed when a message is sent to a server
            """
            if len(message.content.strip()) == 0:
                return

            src_lang = None
            channel = await get_channel(message.channel.id)
            if (len(channel.translate_to)) > 0:
                src_lang = None if channel.locale is None else Language(channel.locale)
                codes = channel.translate_to
            else:
                user = await get_user(message.author.id)
                if len(user.translate_in) > 0 and message.channel.id not in user.translate_in:
                    return

                codes = user.translate_to

            languages = []
            for code in codes:
                if self._translator.is_code_supported(code):
                    languages.append(Language(code))

            if len(languages) == 0:
                return

            await self._send_translation(message, languages, src_lang)

    async def _send_translation(self,
                                message: Message,
                                dest_langs: Iterable[Language],
                                src_lang: Language = None) -> None:
        async with message.channel.typing():
            text = message.content
            if src_lang is None:
                src_lang = Language((await asyncio.to_thread(langid.classify, text))[0])

            if len(message.embeds) != 0:
                text += "\n\n"
                for embed in message.embeds:
                    if embed.description is not None:
                        text += embed.description + "\n\n"

                text = text.removesuffix("\n\n")

            description = ""
            async for translation in self._translator.translate_targets(text, dest_langs, src_lang):
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

    @localization_args(set_languages_all_channels_description_default=str(ALL_CHANNELS_DEFAULT))
    @app_commands.command(name=default_loc.format_value("set-languages-name"),
                          description=default_loc.format_value("set-languages-description"))
    @app_commands.describe(all_channels=default_loc.format_value(
        "set-languages-all-channels-description",
        {"set-languages-all-channels-description-default": str(ALL_CHANNELS_DEFAULT)})
    )
    async def set_languages(self, interaction: Interaction, all_channels: bool = ALL_CHANNELS_DEFAULT):
        """
        Set or remove the languages to be translated for your messages
        """

        loc = Localization(interaction.locale, resources)
        send = await defer_response(interaction)

        language_view = await TranslatorLanguageSelectView(interaction).init()
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

    @localization_args(set_channel_languages_this_channel_description_default=str(THIS_CHANNEL_DEFAULT))
    @app_commands.command(name=default_loc.format_value("set-channel-languages-name"),
                          description=default_loc.format_value("set-channel-languages-description"))
    @app_commands.describe(this_channel=default_loc.format_value(
        "set-channel-languages-this-channel-description",
        {"set-channel-languages-this-channel-description-default": str(THIS_CHANNEL_DEFAULT)})
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel_languages(self, interaction: Interaction, this_channel: bool = THIS_CHANNEL_DEFAULT):
        """
        Set or remove the languages to be translated for channels
        """

        loc = Localization(interaction.locale, resources)
        send = await defer_response(interaction)

        language_view = await TranslatorLanguageSelectView(interaction).init()
        channel_select = await TranslatorChannelSelect(interaction.locale).init()

        async def on_submit(interaction: Interaction):
            channels = [interaction.channel_id] if this_channel else [channel.id for channel in channel_select.values]
            for channel in channels:
                config = await get_channel(channel)
                config.translate_to = list(language_view.selected)
                await set_channel(config)

            await interaction.response.send_message(
                success(await loc.format_value_or_translate("channel-languages-updated")),
                ephemeral=True
            )

        button = await SubmitButton(interaction.locale).init()
        button.callback = on_submit

        if not this_channel:
            language_view.add_item(channel_select)

        language_view.add_item(button)

        await send(view=language_view, ephemeral=True)

    @localization_args(set_channel_main_language_this_channel_description_default=str(THIS_CHANNEL_DEFAULT))
    @app_commands.command(name=default_loc.format_value("set-channel-main-language-name"),
                          description=default_loc.format_value("set-channel-main-language-description"),
                          )
    @app_commands.describe(this_channel=default_loc.format_value(
        "set-channel-main-language-this-channel-description",
        {"set-channel-main-language-this-channel-description-default": str(THIS_CHANNEL_DEFAULT)})
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel_main_language(self, interaction: Interaction, this_channel: bool = THIS_CHANNEL_DEFAULT):
        """
        Set or remove the main language of the channels.
        """

        loc = Localization(interaction.locale, resources)
        send = await defer_response(interaction)

        language_view = await TranslatorLanguageSelectView(interaction, 1).init()
        channel_select = await TranslatorChannelSelect(interaction.locale).init()

        async def on_submit(interaction: Interaction):
            selected = list(language_view.selected)
            channels = [interaction.channel_id] if this_channel else [channel.id for channel in channel_select.values]

            if len(channels) == 0:
                await interaction.response.send_message(
                    error(await loc.format_value_or_translate("no-channels-selected")),
                    ephemeral=True
                )
                return

            for channel in channels:
                config = await get_channel(channel)
                config.locale = selected[0] if len(selected) != 0 else None
                await set_channel(config)

            await interaction.response.send_message(
                success(await loc.format_value_or_translate("channel-main-language-updated")),
                ephemeral=True
            )

        button = await SubmitButton(interaction.locale).init()
        button.disabled = not this_channel
        button.callback = on_submit

        async def on_channel_select(_: Interaction):
            button.disabled = len(channel_select.values) == 0
            await interaction.edit_original_response(view=language_view)

        channel_select.on_select = on_channel_select

        if not this_channel:
            language_view.add_item(channel_select)

        language_view.add_item(button)

        await send(view=language_view, ephemeral=True)
