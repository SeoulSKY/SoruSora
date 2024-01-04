"""
This module implements translator command
"""

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

import langid
from discord import app_commands, Interaction, Message, Embed, HTTPException
from discord.ext.commands import Bot
from discord.ui import View

from firestore import user, channel
from utils import constants, templates, ui
from utils.templates import success


class ChannelLanguageSelect(ui.LanguageSelect):
    """
    Select UI to select available languages for a channel
    """

    async def callback(self, interaction: Interaction):
        config = await channel.get_channel(interaction.channel_id)
        config.translate_to = self.values
        await channel.set_channel(config)

        await interaction.response.send_message(success("This channel's languages to be translated have been updated"),
                                                ephemeral=True)


class BatchTranslator:
    """
    Translator that can translate a text to multiple languages concurrently
    """

    _CODES_TO_LANGUAGES = {v: k for k, v in constants.translator.get_supported_languages(as_dict=True).items()}

    def __init__(self, targets: list[str]):
        languages_to_codes = constants.translator.get_supported_languages(as_dict=True)

        self._translators = (constants.Translator(target=languages_to_codes[target]) for target in targets)
        self._executor = ThreadPoolExecutor(max_workers=len(targets))

    async def translate(self, text: str):
        """
        Translate the text to target languages

        :param text: The text to translate
        :return: List of tuples containing target language code and translated text
        """

        source, _ = langid.classify(text)

        futures = []
        for translator in self._translators:
            if source == translator.target:
                continue

            translator.source = source
            futures.append(self._executor.submit(self._translate, text, translator))

        for future in concurrent.futures.as_completed(futures):
            yield future.result()

    @staticmethod
    def _translate(text: str, translator: constants.Translator) -> tuple[str, str]:
        return BatchTranslator._CODES_TO_LANGUAGES[translator.target], translator.translate(text)


class Translator(app_commands.Group):
    """
    Commands related to translation
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

        self._setup_user_listeners()
        self._setup_channel_listeners()

    def _setup_user_listeners(self):
        async def on_message(message: Message):
            usr = await user.get_user(message.author.id)
            if len(message.content.strip()) == 0 or len(usr.translate_to) == 0:
                return

            await self._send_translation(message, usr.translate_to)

        self.bot.add_listener(on_message)

    def _setup_channel_listeners(self):
        async def on_message(message: Message):
            if message.author == self.bot.user:
                return

            chan = await channel.get_channel(message.channel.id)
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
            for chunk in Translator._split(description, constants.EMBED_DESCRIPTION_MAX_LENGTH):
                embed = Embed(color=templates.color, description=chunk)
                embed.set_footer(text=message.author.display_name, icon_url=message.author.display_avatar.url)
                embeds.append(embed)

            try:
                await message.reply(embeds=embeds[0: min(len(embeds), constants.MAX_NUM_EMBEDS_IN_MESSAGE)],
                                    silent=True)
            except HTTPException as ex:
                if ex.code == 50035:
                    await message.reply(templates.error("Cannot send the translated text because it is too long"),
                                        silent=True)
                    return

                raise ex

    @staticmethod
    def _split(string: str, count: int):
        for i in range(0, len(string), count):
            yield string[i: i + count]

    @app_commands.command()
    async def set_your_languages(self, interaction: Interaction):
        """
        Set languages to be translated for your messages
        """
        view = View()
        view.add_item(ui.LanguageSelect())
        await interaction.response.send_message(view=view, ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel_languages(self, interaction: Interaction):
        """
        Set languages to be translated for this channel
        """
        view = View()
        view.add_item(ChannelLanguageSelect())
        await interaction.response.send_message(view=view, ephemeral=True)

    @app_commands.command()
    async def clear_your_languages(self, interaction: Interaction):
        """
        Clear languages to be translated for your messages
        """
        config = await user.get_user(interaction.user.id)
        config.translate_to = []
        await user.set_user(config)

        await interaction.response.send_message(success("Your languages to be translated have been cleared"),
                                                ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_channel_languages(self, interaction: Interaction):
        """
        Clear languages to be translated for this channel
        """
        config = await channel.get_channel(interaction.channel_id)
        config.translate_to = []
        await channel.set_channel(config)

        await interaction.response.send_message(success("This channel's languages to be translated have been cleared"),
                                                ephemeral=True)
