"""
Implements a command relate to AI chat
"""
import asyncio
import os
import re
import json

from discord import app_commands, Message, Interaction
from discord.ext.commands import Bot
from characterai import PyAsyncCAI
from characterai.errors import PyCAIError

import firestore.user
from templates import success, warning


class Chat(app_commands.Group):
    """
    Commands related to AI chats
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self._client = PyAsyncCAI(os.getenv("CAI_TOKEN"))

        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._client.start())

        task = loop.create_task(self._client.character.info(os.getenv("CAI_CHAR_ID")))
        response: dict = loop.run_until_complete(task)
        if response.get("status") != "OK":
            raise PyCAIError(f"Unexpected format of response:\n{json.dumps(response, indent=1)}")

        self._char_info = response["character"]
        loop.close()

        async def _listener():
            await self._client.start()
            self.bot.remove_listener(_listener, "on_ready")

        self.bot.add_listener(_listener, "on_ready")

        self._setup_chat_listeners()

    def _setup_chat_listeners(self):
        async def _listener(message: Message):
            if message.author.bot:
                return
            if self.bot.user not in message.mentions and (
                    message.reference is None or message.reference.resolved.author != self.bot):
                return

            await self._send_message(message)

        self.bot.add_listener(_listener, "on_message")

    async def _send_message(self, message: Message):
        await message.channel.typing()

        user = await firestore.user.get_user(message.author.id)
        if user.chat_history_id is None:
            response = await self._client.chat.new_chat(self._char_info["external_id"])
            user.chat_history_id = response["external_id"]

            for participant in response["participants"]:
                if participant["is_human"]:
                    user.chat_history_tgt = participant["user"]["username"]

            if user.chat_history_tgt is None:
                # at least one of the participants must be non-human
                raise PyCAIError(f"Unexpected format of response:\n{json.dumps(response, indent=1)}")

            await firestore.user.set_user(user)

        content = message.content.removeprefix(self.bot.user.mention).strip()
        text = re.compile(re.escape(self.bot.user.display_name), re.IGNORECASE).sub(self._char_info["name"], content)

        response: dict = await self._client.chat.send_message(self._char_info["external_id"], text,
                                                              history_external_id=user.chat_history_id,
                                                              tgt=user.chat_history_tgt)
        reply = response["replies"][0]["text"]
        content = re.compile(re.escape(self._char_info["name"]), re.IGNORECASE).sub(self.bot.user.display_name, reply)
        await message.reply(content)

    @app_commands.command()
    async def clear(self, interaction: Interaction):
        """
        Clear the chat history between you and this bot
        """
        user = await firestore.user.get_user(interaction.user.id)
        if user.chat_history_id is None:
            await interaction.response.send_message(warning(f"You don't have any conversations with "
                                                            f"{interaction.client.user.display_name}"), ephemeral=True)
            return

        response: dict = await self._client.chat.get_history(user.chat_history_id)

        uuids = []
        for message in response["messages"]:
            uuids.append(message["uuid"])

        await self._client.chat.delete_message(user.chat_history_id, uuids)
        user.chat_history_id = None
        user.chat_history_tgt = None
        await firestore.user.set_user(user)

        await interaction.response.send_message(success("Deleted!"), ephemeral=True)
