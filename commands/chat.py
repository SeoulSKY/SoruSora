"""
Implements a command relate to AI chat
"""
import asyncio
import os
import re
import json

from discord import app_commands, Message
from discord.ext.commands import Bot
from characterai import PyAsyncCAI
from characterai.errors import PyCAIError


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
        content = message.content.removeprefix(self.bot.user.mention).strip()
        text = re.compile(re.escape(self.bot.user.display_name), re.IGNORECASE).sub(self._char_info["name"], content)

        response: dict = await self._client.chat.send_message(self._char_info["external_id"], text)
        reply = response["replies"][0]["text"]
        content = re.compile(re.escape(self._char_info["name"]), re.IGNORECASE).sub(self.bot.user.display_name, reply)
        await message.reply(content)
