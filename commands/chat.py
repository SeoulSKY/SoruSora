"""
Implements a command relate to AI chat
"""
import asyncio
import os

from characterai import PyAsyncCAI
from characterai.errors import NoResponse, FilterError
from deep_translator import GoogleTranslator
from discord import app_commands, Message, Interaction
from discord.ext.commands import Bot
from langid import langid

import firestore.user
from templates import info, success, error, warning


class Chat(app_commands.Group):
    """
    Commands related to AI chats
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self._client = PyAsyncCAI(os.getenv("CAI_TOKEN"))
        self._char_info = None
        self._is_ready = asyncio.Event()

        async def on_ready():
            await self._client.start()
            response = await self._client.character.info(os.getenv("CAI_CHAR_ID"), wait=True)
            self._char_info = response["character"]
            self._is_ready.set()

        self.bot.add_listener(on_ready)

        self._setup_chat_listeners()

    def _setup_chat_listeners(self):
        async def on_message(message: Message):
            if message.author.bot:
                return
            if self.bot.user not in message.mentions and (
                    message.reference is None or message.reference.resolved.author != self.bot):
                return
            if not self._is_ready.is_set():
                await message.reply(self._overloaded_message())
                return

            await self._send_message(message)

        self.bot.add_listener(on_message)

    def _overloaded_message(self) -> str:
        return info(f"Looks like {self.bot.user.display_name} has turned on the Do Not Disturb mode. "
                    "Let's talk to her later")

    async def _send_message(self, message: Message):
        async with message.channel.typing():
            user = await firestore.user.get_user(message.author.id)
            if user.chat_history_id is None:
                response = await self._client.chat.new_chat(self._char_info["external_id"])
                user.chat_history_id = response["external_id"]

                instruction = f"(OCC: Your name is {self.bot.user.display_name} and you are a Discord bot made by " \
                              f"SeoulSKY. The name of the Discord server you are in is {message.guild.name}. " \
                              f"You like playing rhythm games. My name is {message.author.display_name})"
                try:
                    await self._send_request(instruction, user)
                except NoResponse:
                    await message.reply(self._overloaded_message())
                    return

                await firestore.user.set_user(user)

            text = message.content.removeprefix(self.bot.user.mention).strip()
            source_lang, _ = langid.classify(text)
            if source_lang != "en":
                translator = GoogleTranslator(source_lang)
                text = await asyncio.to_thread(translator.translate, text)

            try:
                content = await self._send_request(text, user, source_lang)
            except NoResponse:
                await message.reply(self._overloaded_message())
                return
            except FilterError:
                await message.reply(
                    warning("Your message might contain inappropriate content. Try to be more respectful"))
                return

            await message.reply(content)

    async def _send_request(self, text: str, user: firestore.user.User, dest_lang="en"):
        response = await self._client.chat.send_message(user.chat_history_id,
                                                        self._char_info["participant__user__username"], text)

        content = response["replies"][0]["text"]
        if dest_lang != "en":
            translator = GoogleTranslator("en", dest_lang)
            content = await asyncio.to_thread(translator.translate, content)

        return content

    @app_commands.command()
    async def clear(self, interaction: Interaction):
        """
        Clear the chat history between you and this bot
        """
        user = await firestore.user.get_user(interaction.user.id)
        if user.chat_history_id is None:
            await interaction.response.send_message(error(f"You don't have any conversations with "
                                                          f"{interaction.client.user.display_name}"), ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        response: dict = await self._client.chat.get_history(user.chat_history_id)

        uuids = []
        for message in response["messages"]:
            uuids.append(message["uuid"])

        await self._client.chat.delete_message(user.chat_history_id, uuids, wait=True)
        user.chat_history_id = None
        user.chat_history_tgt = None
        await firestore.user.set_user(user)

        await interaction.followup.send(success("Deleted!"), ephemeral=True)
