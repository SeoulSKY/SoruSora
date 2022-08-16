from typing import Coroutine, Callable

import discord.ui
import googletrans
from discord import app_commands, Interaction, Message, SelectOption
from discord.ext.commands import Bot
from discord.ui import View

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

        super().__init__(placeholder="Select languages that will be translated to", max_values=min(25, len(languages)),
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

            translator = googletrans.Translator()
            results: list[str] = []
            for dest in (await configs.get(message.author.id)).translate_to:
                result = translator.translate(message.content, dest=dest)
                if result.src != result.dest:
                    results.append(result.text)

            await message.reply("**Translated:**\n\n" + "\n\n".join(results))

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

    @app_commands.command()
    async def select_languages(self, interaction: Interaction):
        """
        Select destination languages of the translator
        """
        view = View()
        view.add_item(LanguageSelect())
        await interaction.response.send_message(view=view, ephemeral=True)
