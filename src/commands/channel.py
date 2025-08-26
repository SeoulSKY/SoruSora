"""Commands related to channel settings."""

from pathlib import Path

from discord import Interaction, app_commands
from discord.ext.commands import Bot

from commands import command
from commands.translator import TranslatorChannelSelect, TranslatorLanguageSelectView
from mongo.channel import get_channel, set_channel
from utils import defer_response
from utils.templates import error, success
from utils.translator import DEFAULT_LANGUAGE, Localization
from utils.ui import SubmitButton

resources = [Path("commands") / "channel.ftl"]

default_loc = Localization(DEFAULT_LANGUAGE, resources)

THIS_DEFAULT = True


@app_commands.default_permissions(manage_channels=True, manage_threads=True)
class Channel(app_commands.Group):
    """Commands related to channel settings."""

    def __init__(self, bot: Bot) -> None:
        """Initialize Channel Command."""
        super().__init__()

        self.bot = bot

    @command(translator_this_description_default=str(THIS_DEFAULT))
    @app_commands.describe(
        this=default_loc.format_value(
            "translator-this-description",
            {"translator-this-description-default": str(THIS_DEFAULT)},
        )
    )
    async def translator(
        self, interaction: Interaction, this: bool = THIS_DEFAULT  # noqa: FBT001
    ) -> None:
        """Set or remove the languages to be translated for channels."""
        loc = Localization(interaction.locale, resources)
        send = await defer_response(interaction)

        language_view = await TranslatorLanguageSelectView(interaction).init()
        channel_select = await TranslatorChannelSelect(interaction.locale).init()

        async def on_submit(interaction: Interaction) -> None:
            channels = (
                [interaction.channel_id]
                if this
                else [channel.id for channel in channel_select.values]  # noqa: PD011
            )
            for channel in channels:
                config = await get_channel(channel)
                config.translate_to = list(language_view.selected)
                await set_channel(config)

            await interaction.response.send_message(
                success(await loc.format_value_or_translate("translator-set")),
                ephemeral=True,
            )

        button = await SubmitButton(interaction.locale).init()
        button.callback = on_submit

        if not this:
            language_view.add_item(channel_select)

        language_view.add_item(button)

        await send(view=language_view, ephemeral=True)

    @command(language_this_description_default=str(THIS_DEFAULT))
    @app_commands.describe(
        this=default_loc.format_value(
            "language-this-description",
            {"language-this-description-default": str(THIS_DEFAULT)},
        )
    )
    async def language(
        self, interaction: Interaction, this: bool = THIS_DEFAULT  # noqa: FBT001
    ) -> None:
        """Set or remove the main language of the channels."""
        loc = Localization(interaction.locale, resources)
        send = await defer_response(interaction)

        language_view = await TranslatorLanguageSelectView(interaction, 1).init()
        channel_select = await TranslatorChannelSelect(interaction.locale).init()

        async def on_submit(interaction: Interaction) -> None:
            selected = list(language_view.selected)
            channels = (
                [interaction.channel_id]
                if this
                else [channel.id for channel in channel_select.values]  # noqa: PD011
            )

            if len(channels) == 0:
                await interaction.response.send_message(
                    error(await loc.format_value_or_translate("no-channels-selected")),
                    ephemeral=True,
                )
                return

            for channel in channels:
                config = await get_channel(channel)
                config.locale = selected[0] if len(selected) != 0 else None
                await set_channel(config)

            await interaction.response.send_message(
                success(await loc.format_value_or_translate("language-set")),
                ephemeral=True,
            )

        button = await SubmitButton(interaction.locale).init()
        button.disabled = not this
        button.callback = on_submit

        async def on_channel_select(_: Interaction) -> None:
            button.disabled = len(channel_select.values) == 0
            await interaction.edit_original_response(view=language_view)

        channel_select.on_select = on_channel_select

        if not this:
            language_view.add_item(channel_select)

        language_view.add_item(button)

        await send(view=language_view, ephemeral=True)
