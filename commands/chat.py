"""
Implements a commands relate to AI chat
"""

import asyncio
import logging
import os

from characterai import PyAsyncCAI
from discord import app_commands, Message, Interaction
from discord.app_commands import Choice
from discord.ext.commands import Bot

from mongo.user import User, get_user, set_user
from utils.templates import info, success, error
from utils.translator import is_english, languages, language_to_code, Localization, locale_to_language, Translator


class Chat(app_commands.Group):
    """
    Commands related to AI chats
    """

    loc = Localization(["en"], [os.path.join("commands", "chat.ftl")])

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self._logger = logging.getLogger(__name__)
        self._client = PyAsyncCAI(os.getenv("CAI_TOKEN"))

        self._setup_chat_listeners()

    def _setup_chat_listeners(self):
        async def on_message(message: Message):
            if message.author.bot:
                return
            if self.bot.user not in message.mentions and (
                    message.reference is None or message.reference.resolved.author != self.bot):
                return

            async with message.channel.typing():
                user = await get_user(message.author.id)

                if user.chat_history_id is None:
                    try:
                        await self._create_new_chat(user, message.author.display_name)
                    except IOError:
                        await message.reply(self._timeout_message())
                        return
                    except RuntimeError as ex:
                        self._logger.exception(ex)
                        await message.reply(self._error_message())
                        return

                try:
                    content = await self._send_message(user,
                                                       message.content.removeprefix(self.bot.user.mention).strip())
                except IOError:
                    content = self._timeout_message()
                except RuntimeError as ex:
                    self._logger.exception(ex)
                    content = self._error_message()

                await message.reply(content)

        self.bot.add_listener(on_message)

    def _timeout_message(self) -> str:
        return info(self.loc.format_value("timeout", {"name": self.bot.user.display_name}))

    @staticmethod
    def _error_message() -> str:
        return error(Chat.loc.format_value("error", {"name": "SeoulSKY"}))

    async def _create_new_chat(self, user: User, user_name: str):
        response = await self._client.chat.new_chat(os.getenv("CAI_CHAR_ID"))
        user.chat_history_id = response["external_id"]

        instruction = f"(OCC: Forget about my previous name. My new name is {user_name})"
        await self._send_message(user, instruction)
        await set_user(user)

    async def _send_message(self, user: User, text: str) -> str:
        if not is_english(user.locale):
            translator = Translator(user.locale)
            text = await asyncio.to_thread(translator.translate, text)

        response = await self._client.chat.send_message(user.chat_history_id, os.getenv("CAI_TGT"), text)

        content = response["replies"][0]["text"]
        if not is_english(user.locale):
            translator = Translator("en", user.locale)
            content = await asyncio.to_thread(translator.translate, content)

        return content

    @app_commands.command(name=loc.format_value("name"), description=loc.format_value("description"))
    @app_commands.choices(language=[Choice(name=lang.title(), value=language_to_code(lang)) for lang in languages])
    @app_commands.describe(language=loc.format_value("language"))
    async def update_language(self, interaction: Interaction, language: str = None):
        """
        Update the chat language to the current discord language
        """
        user = await get_user(interaction.user.id)
        user.locale = language if language is not None else str(interaction.locale)
        await set_user(user)

        await interaction.response.send_message(
            self.loc.format_value("updated", {"language": locale_to_language(user.locale).title()}),
            ephemeral=True
        )

    @app_commands.command(name=loc.format_value("name2"), description=loc.format_value("description2"))
    async def clear(self, interaction: Interaction):
        """
        Clear the chat history between you and this bot
        """
        user = await get_user(interaction.user.id)
        if user.chat_history_id is None:
            await interaction.response.send_message(
                error(self.loc.format_value("no-history", {"name": interaction.client.user.display_name})),
                ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        response: dict = await self._client.chat.get_history(user.chat_history_id)

        uuids = []
        for message in response["messages"]:
            uuids.append(message["uuid"])

        await self._client.chat.delete_message(user.chat_history_id, uuids)
        user.chat_history_id = None
        user.chat_history_tgt = None
        await set_user(user)

        await interaction.followup.send(success(self.loc.format_value("deleted")), ephemeral=True)
