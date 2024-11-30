"""Implements translator commands."""

import asyncio
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Any

import langid
from discord import Embed, HTTPException, Interaction, Locale, Message, app_commands
from discord.ext.commands import Bot

from commands import command
from mongo.channel import get_channel
from mongo.user import get_user, set_user
from utils import defer_response, templates
from utils.constants import ErrorCode, Limit
from utils.templates import success
from utils.translator import DEFAULT_LANGUAGE, Language, Localization, get_translator
from utils.ui import ChannelSelect, LanguageSelectView, SubmitButton

resources = [Path("commands") / "translator.ftl"]
default_loc = Localization(DEFAULT_LANGUAGE, resources)

ALL_CHANNELS_DEFAULT = True


class TranslatorLanguageSelectView(LanguageSelectView):
    """Select UI to select available languages for a translator."""

    def __init__(self, interaction: Interaction, max_values: int | None = None) -> None:
        """Create a view to select languages for a translator
        :param interaction: The interaction of the command
        :param max_values: Maximum number of values that can be selected.
        """
        loc = Localization(interaction.locale, resources)
        super().__init__(
            interaction, loc.format_value_or_translate("select-languages"), max_values
        )


class TranslatorChannelSelect(ChannelSelect):
    """Select UI to select channels for a translator."""

    def __init__(self, locale: Locale) -> None:
        """Create a view to select channels for a translator
        :param locale: The locale of the user.
        """
        loc = Localization(locale, resources)
        super().__init__(placeholder=loc.format_value_or_translate("select-channels"))


_translator = get_translator()


def setup(bot: Bot) -> None:
    """Set up the translator commands."""

    async def on_message(message: Message) -> None:
        if len(message.content.strip()) == 0 or message.author == bot.user:
            return

        channel = await get_channel(message.channel.id)
        src_lang = None

        if len(channel.translate_to) > 0:
            codes = channel.translate_to
            src_lang = Language(channel.locale) if channel.locale else None
        else:
            user = await get_user(message.author.id)
            codes = (
                user.translate_to
                if len(user.translate_in) == 0
                or message.channel.id in user.translate_in
                else []
            )

        languages = [Language(code) for code in codes if
                     _translator.is_code_supported(code)]

        if len(languages) == 0:
            return

        await _send_translation(message, languages, src_lang)

    bot.add_listener(on_message)


async def _send_translation(  # noqa: C901
    message: Message, dest_langs: Iterable[Language], src_lang: Language = None
) -> None:
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
        async for translation in _translator.translate_targets(
            text, dest_langs, src_lang
        ):
            if translation.source == translation.target:
                continue

            description += f"**__{translation.target.name}__**\n{translation.text}\n\n"

        description.removesuffix("\n\n")

        if len(description) == 0:
            return

        embeds = []
        for chunk in _split(description, int(Limit.EMBED_DESCRIPTION_LEN)):
            embed = Embed(color=templates.color, description=chunk)
            embed.set_footer(
                text=message.author.display_name,
                icon_url=message.author.display_avatar.url,
            )
            embeds.append(embed)

        try:
            await message.reply(
                embeds=embeds[0 : min(len(embeds), int(Limit.NUM_EMBEDS_IN_MESSAGE))],
                silent=True,
            )
        except HTTPException as ex:
            if ex.code == ErrorCode.MESSAGE_TOO_LONG:
                await message.reply(
                    templates.error(
                        "Cannot send the translated text because it is too long"
                    ),
                    silent=True,
                )
                return

            raise


def _split(string: str, count: int) -> Generator[str, Any, None]:
    for i in range(0, len(string), count):
        yield string[i : i + count]


@command(translator_all_channels_description_default=str(ALL_CHANNELS_DEFAULT))
@app_commands.describe(
    all_channels=default_loc.format_value(
        "translator-all-channels-description",
        {"translator-all-channels-description-default": str(ALL_CHANNELS_DEFAULT)},
    )
)
async def translator(
    interaction: Interaction, all_channels: bool = ALL_CHANNELS_DEFAULT  # noqa: FBT001
) -> None:
    """Set or remove the languages to be translated for your messages."""
    loc = Localization(interaction.locale, resources)
    send = await defer_response(interaction)

    language_view = await TranslatorLanguageSelectView(interaction).init()
    channel_select = await TranslatorChannelSelect(interaction.locale).init()

    async def on_submit(interaction: Interaction) -> None:
        user = await get_user(interaction.user.id)
        user.translate_to = list(language_view.selected)
        user.translate_in = (
            [] if all_channels else [channel.id for channel in channel_select.values]  # noqa: PD011
        )
        await set_user(user)

        # pylint: disable=duplicate-code
        await interaction.response.send_message(
            success(await loc.format_value_or_translate("translator-set")),
            ephemeral=True,
        )

    button = await SubmitButton(interaction.locale).init()
    button.callback = on_submit

    if not all_channels:
        language_view.add_item(channel_select)

    language_view.add_item(button)

    await send(view=language_view, ephemeral=True)
