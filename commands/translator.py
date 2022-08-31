"""
This module implements translator command
"""

import concurrent.futures

import discord.ui
import googletrans
from discord import app_commands, Interaction, Message, SelectOption, Embed, HTTPException
from discord.ext.commands import Bot
from discord.ui import View

import constants
import templates
from firestore import user, channel
from templates import success


class LanguageSelect(discord.ui.Select):
    """
    Select UI to select available languages for a user
    """

    def __init__(self):
        languages = [
            "chinese (simplified)",
            "chinese (traditional)",
            "english",
            "filipino",
            "french",
            "german",
            "indonesian",
            "italian",
            "japanese",
            "korean",
            "malay",
            "russian",
            "spanish",
            "thai",
            "vietnamese"
        ]

        languages = [SelectOption(label=lang) for lang in languages]

        max_value_possible = 25
        super().__init__(placeholder="Select languages that will be translated to",
                         max_values=min(max_value_possible, len(languages)),
                         options=languages)

    async def callback(self, interaction: Interaction):
        config = await user.get_user(interaction.user.id)
        config.translate_to = self.values
        await user.set_user(config)

        await interaction.response.send_message(success("Your destination languages have been updated"), ephemeral=True)


class ChannelLanguageSelect(LanguageSelect):
    """
    Select UI to select available languages for a channel
    """

    async def callback(self, interaction: Interaction):
        config = await channel.get_channel(interaction.channel_id)
        config.translate_to = self.values
        await channel.set_channel(config)

        await interaction.response.send_message(success("Destination languages of this channel have been updated"),
                                                ephemeral=True)


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
            if len(usr.translate_to) == 0:
                return

            await self._send_translation(message, usr.translate_to)

        self.bot.add_listener(on_message)

    def _setup_channel_listeners(self):
        async def on_message(message: Message):
            if message.author == self.bot.user:
                return

            chan = await channel.get_channel(message.channel.id)
            if len(chan.translate_to) == 0:
                return

            await self._send_translation(message, chan.translate_to)

        self.bot.add_listener(on_message)

    @staticmethod
    async def _send_translation(message: Message, dest_langs: list[str]):
        description = "\n\n".join(Translator._translate(message, dest_langs))
        embeds = []
        for chunk in Translator._split(description, constants.EMBED_DESCRIPTION_MAX_LENGTH):
            embed = Embed(color=templates.color, description=chunk)
            embed.set_footer(text=message.author.display_name, icon_url=message.author.display_avatar.url)
            embeds.append(embed)

        try:
            await message.reply(embeds=embeds[0: min(len(embeds), constants.MAX_NUM_EMBEDS_IN_MESSAGE)])
        except HTTPException as ex:
            if ex.code == 50035:
                await message.reply(templates.error("Failed to translate because the content is too long"))
                return

            raise ex

    @staticmethod
    def _translate(message: Message, dest_langs: list[str]):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(dest_langs))
        translator = googletrans.Translator()
        futures = []

        for dest_lang in dest_langs:
            text = message.content

            if len(message.embeds) != 0:
                text += "\n\n"
                for embed in message.embeds:
                    text += embed.description

            futures.append(executor.submit(translator.translate, text=text, dest=dest_lang))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result.src != result.dest:
                yield f"**__{googletrans.LANGUAGES.get(result.dest).capitalize()}__**\n{result.text}"

    @staticmethod
    def _split(string: str, count: int):
        for i in range(0, len(string), count):
            yield string[i: i + count]

    @app_commands.command()
    async def set_your_languages(self, interaction: Interaction):
        """
        Set destination languages of the translator for your messages
        """
        view = View()
        view.add_item(LanguageSelect())
        await interaction.response.send_message(view=view, ephemeral=True)

    @app_commands.command()
    async def clear_your_languages(self, interaction: Interaction):
        """
        Clear destination languages of the translator for your messages
        """
        usr = await user.get_user(interaction.user.id)
        usr.translate_to = []
        await user.set_user(usr)

        await interaction.response.send_message(success("Your destination languages have been removed"), ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel_languages(self, interaction: Interaction):
        """
        Set destination languages of the translator for this channel
        """
        view = View()
        view.add_item(ChannelLanguageSelect())
        await interaction.response.send_message(view=view, ephemeral=True)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_channel_languages(self, interaction: Interaction):
        """
        Clear destination languages of the translator for this channel
        """
        chan = await channel.get_channel(interaction.channel_id)
        chan.translate_to = []
        await channel.set_channel(chan)

        await interaction.response.send_message(success("Destination languages of this channel have been removed"),
                                                ephemeral=True)
