import concurrent.futures
from typing import Coroutine, Callable

import discord.ui
import googletrans
from discord import app_commands, Interaction, Message, SelectOption, Embed, HTTPException
from discord.ext.commands import Bot
from discord.ui import View

import constants
import templates
from firestore import configs
from templates import success


class LanguageSelect(discord.ui.Select):

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

        languages = [SelectOption(label=lang, value=googletrans.LANGCODES.get(lang)) for lang in languages]

        max_value_possible = 25
        super().__init__(placeholder="Select languages that will be translated to",
                         max_values=min(max_value_possible, len(languages)),
                         options=languages)

    async def callback(self, interaction: Interaction):
        config = await configs.get(interaction.user.id)
        config.translate_to = self.values
        await configs.set(config)

        await interaction.response.send_message(success("Your destination languages have been updated"), ephemeral=True)


class Translator(app_commands.Group):
    """
    Translate messages you send
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.message_listeners: dict[int, Callable[[Message], Coroutine]] = {}

    @app_commands.command()
    async def toggle(self, interaction: Interaction):
        """
        Toggle translator for your account
        """

        if not await configs.have(interaction.user.id):
            config = configs.Config(interaction.user.id, True)
        else:
            config = await configs.get(interaction.user.id)
            config.is_translator_on = not config.is_translator_on

        async def on_message(message: Message):
            if message.author != interaction.user:
                return

            dest_langs = (await configs.get(message.author.id)).translate_to

            executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(dest_langs))
            translator = googletrans.Translator()

            futures = [executor.submit(lambda: translator.translate(message.content, dest=dest)) for dest in dest_langs]
            results: list[str] = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result.src != result.dest:
                    results.append(f"**__{googletrans.LANGUAGES.get(result.dest).capitalize()}__**\n{result.text}")

            description = "\n\n".join(results)
            embeds = []
            for chunk in self._split(description, constants.EMBED_DESCRIPTION_MAX_LENGTH):
                embed = Embed(color=templates.color, description=chunk)
                embed.set_footer(text=message.author.display_name, icon_url=message.author.display_avatar.url)
                embeds.append(embed)

            try:
                await message.reply(embeds=embeds[0: min(len(embeds), constants.MAX_NUM_EMBEDS_IN_MESSAGE)])
            except HTTPException as e:
                if e.status == 400:
                    await message.reply(templates.error("Failed to translate because the content is too long"))
                    return

                raise e

        if config.is_translator_on:
            self.bot.add_listener(on_message)
            self.message_listeners[interaction.user.id] = on_message
        else:
            if interaction.user.id in self.message_listeners:
                self.bot.remove_listener(self.message_listeners[interaction.user.id])
                self.message_listeners.pop(interaction.user.id)

        await configs.set(config)
        toggle_value = "on" if config.is_translator_on else "off"
        await interaction.response.send_message(success(f"Translator has been set to `{toggle_value}`"), ephemeral=True)

    @staticmethod
    def _split(string: str, count: int):
        for i in range(0, len(string), count):
            yield string[i: i + count]

    @app_commands.command()
    async def select_languages(self, interaction: Interaction):
        """
        Select destination languages of the translator
        """
        view = View()
        view.add_item(LanguageSelect())
        await interaction.response.send_message(view=view, ephemeral=True)
