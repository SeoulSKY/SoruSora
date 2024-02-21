"""
This module implements translator commands
"""
import os

from discord import app_commands, Interaction, Message, Embed, HTTPException, Locale
from discord.ext.commands import Bot
from discord.ui import View

from mongo.channel import get_channel, set_channel
from mongo.user import get_user, set_user
from utils import templates, ui
from utils.constants import ErrorCode, Limit
from utils.templates import success
from utils.translator import BatchTranslator, locale_to_code, Localization


class ChannelLanguageSelect(ui.LanguageSelect):
    """
    Select UI to select available languages for a channel
    """

    def __init__(self, locale: Locale):
        self.localization = Localization([locale_to_code(locale)],
                                         [os.path.join("commands", "translator.ftl")])
        super().__init__(self.localization.format_value("select-channel-languages"))

    async def callback(self, interaction: Interaction):
        config = await get_channel(interaction.channel_id)
        config.translate_to = self.values
        await set_channel(config)

        await interaction.response.send_message(
            success(self.localization.format_value("channel-languages-updated")), ephemeral=True
        )


class UserLanguageSelect(ui.LanguageSelect):
    """
    Select UI to select available languages for a user
    """

    def __init__(self, locale: Locale):
        self.loc = Localization([locale_to_code(locale)],
                                [os.path.join("commands", "translator.ftl")])
        super().__init__(self.loc.format_value("select-your-languages"))

    async def callback(self, interaction: Interaction):
        config = await get_user(interaction.user.id)
        config.translate_to = self.values
        await set_user(config)

        await interaction.response.send_message(
            success(self.loc.format_value("your-languages-updated")), ephemeral=True
        )


class Translator(app_commands.Group):
    """
    Commands related to translation
    """

    doc = Localization(["en"], [os.path.join("commands", "translator.ftl")])

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

        self._setup_user_listeners()
        self._setup_channel_listeners()

    def _setup_user_listeners(self):
        async def on_message(message: Message):
            usr = await get_user(message.author.id)
            if len(message.content.strip()) == 0 or len(usr.translate_to) == 0:
                return

            await self._send_translation(message, usr.translate_to)

        self.bot.add_listener(on_message)

    def _setup_channel_listeners(self):
        async def on_message(message: Message):
            if message.author == self.bot.user:
                return

            chan = await get_channel(message.channel.id)
            if len(message.content.strip()) == 0 or len(chan.translate_to) == 0:
                return

            await self._send_translation(message, chan.translate_to)

        self.bot.add_listener(on_message)

    @staticmethod
    async def _send_translation(message: Message, dest_langs: list[str]):
        async with message.channel.typing():
            text = message.content

            if len(message.embeds) != 0:
                text += "\n\n"
                for embed in message.embeds:
                    if embed.description is not None:
                        text += embed.description + "\n\n"

                text = text.removesuffix("\n\n")

            description = ""
            translator = BatchTranslator(dest_langs)
            async for target, translated in translator.translate(text):
                description += f"**__{target.title()}__**\n{translated}\n\n"

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

    @app_commands.command(name=doc.format_value("name"), description=doc.format_value("description"))
    async def set_your_languages(self, interaction: Interaction):
        """
        Set languages to be translated for your messages
        """
        view = View()
        view.add_item(UserLanguageSelect(interaction.locale))
        await interaction.response.send_message(view=view, ephemeral=True)

    @app_commands.command(name=doc.format_value("name2"), description=doc.format_value("description2"))
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel_languages(self, interaction: Interaction):
        """
        Set languages to be translated for this channel
        """
        view = View()
        view.add_item(ChannelLanguageSelect(interaction.locale))
        await interaction.response.send_message(view=view, ephemeral=True)

    @app_commands.command(name=doc.format_value("name3"), description=doc.format_value("description3"))
    async def clear_your_languages(self, interaction: Interaction):
        """
        Clear languages to be translated for your messages
        """
        user = await get_user(interaction.user.id)
        user.translate_to = []
        await set_user(user)

        await interaction.response.send_message(success(self.doc.format_value("your-languages-cleared")),
                                                ephemeral=True)

    @app_commands.command(name=doc.format_value("name4"), description=doc.format_value("description4"))
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_channel_languages(self, interaction: Interaction):
        """
        Clear languages to be translated for this channel
        """
        channel = await get_channel(interaction.channel_id)
        channel.translate_to = []
        await set_channel(channel)

        await interaction.response.send_message(success(self.doc.format_value("channel-languages-cleared")),
                                                ephemeral=True)
