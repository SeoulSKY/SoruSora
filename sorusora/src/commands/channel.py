"""
Commands related to channel settings
"""

import os

from discord import app_commands, Interaction

from commands import update_locale
from commands.translator import TranslatorLanguageSelectView, TranslatorChannelSelect
from mongo.channel import set_channel, get_channel
from utils import defer_response
from utils.templates import success, error
from utils.translator import format_localization, Localization, DEFAULT_LANGUAGE
from utils.ui import SubmitButton

resources = [os.path.join("commands", "channel.ftl")]

default_loc = Localization(DEFAULT_LANGUAGE, resources)

THIS_DEFAULT = True


@app_commands.default_permissions(manage_channels=True, manage_threads=True)
class Channel(app_commands.Group):
    """
    Commands related to channel settings
    """

    def __init__(self, bot):
        super().__init__()

        self.bot = bot

    @format_localization(translator_this_description_default=str(THIS_DEFAULT))
    @app_commands.command(name=default_loc.format_value("translator-name"),
                          description=default_loc.format_value("translator-description"))
    @app_commands.describe(this=default_loc.format_value(
        "translator-this-description",
        {"translator-this-description-default": str(THIS_DEFAULT)})
    )
    @update_locale()
    async def translator(self, interaction: Interaction, this: bool = THIS_DEFAULT):
        """
        Set or remove the languages to be translated for channels
        """

        loc = Localization(interaction.locale, resources)
        send = await defer_response(interaction)

        language_view = await TranslatorLanguageSelectView(interaction).init()
        channel_select = await TranslatorChannelSelect(interaction.locale).init()

        async def on_submit(interaction: Interaction):
            channels = [interaction.channel_id] if this else [channel.id for channel in channel_select.values]
            for channel in channels:
                config = await get_channel(channel)
                config.translate_to = list(language_view.selected)
                await set_channel(config)

            await interaction.response.send_message(
                success(await loc.format_value_or_translate("translator-set")),
                ephemeral=True
            )

        button = await SubmitButton(interaction.locale).init()
        button.callback = on_submit

        if not this:
            language_view.add_item(channel_select)

        language_view.add_item(button)

        await send(view=language_view, ephemeral=True)

    @format_localization(language_this_description_default=THIS_DEFAULT)
    @app_commands.command(name=default_loc.format_value("language-name"),
                          description=default_loc.format_value("language-description"))
    @app_commands.describe(this=default_loc.format_value(
        "language-this-description",
        {"language-this-description-default": str(THIS_DEFAULT)})
    )
    @update_locale()
    async def language(self, interaction: Interaction, this: bool = THIS_DEFAULT):
        """
        Set or remove the main language of the channels.
        """

        loc = Localization(interaction.locale, resources)
        send = await defer_response(interaction)

        language_view = await TranslatorLanguageSelectView(interaction, 1).init()
        channel_select = await TranslatorChannelSelect(interaction.locale).init()

        async def on_submit(interaction: Interaction):
            selected = list(language_view.selected)
            channels = [interaction.channel_id] if this else [channel.id for channel in channel_select.values]

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
                success(await loc.format_value_or_translate("language-set")),
                ephemeral=True
            )

        button = await SubmitButton(interaction.locale).init()
        button.disabled = not this
        button.callback = on_submit

        async def on_channel_select(_: Interaction):
            button.disabled = len(channel_select.values) == 0
            await interaction.edit_original_response(view=language_view)

        channel_select.on_select = on_channel_select

        if not this:
            language_view.add_item(channel_select)

        language_view.add_item(button)

        await send(view=language_view, ephemeral=True)
