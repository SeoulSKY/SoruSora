"""
Implements a command relate to AI chat
"""

import asyncio
import logging
import os

from characterai import PyAsyncCAI
from characterai.errors import FilterError
from deep_translator import GoogleTranslator
from discord import app_commands, Message, Interaction
from discord.ext.commands import Bot
from discord.ui import View

import firestore.user
from utils import ui
from utils.templates import info, success, error, warning


class MainLanguageSelect(ui.LanguageSelect):
    """
    Select UI to select the main language of a user
    """

    def __init__(self):
        super().__init__(min_values=1, max_values=1, placeholder="Select the chat language")

    async def callback(self, interaction: Interaction):
        config = await firestore.user.get_user(interaction.user.id)
        config.main_language = self.values[0]
        await firestore.user.set_user(config)

        await interaction.response.send_message(success("Your chat language has been updated"), ephemeral=True)


class Chat(app_commands.Group):
    """
    Commands related to AI chats
    """

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
                user = await firestore.user.get_user(message.author.id)
                if user.chat_history_id is None:
                    try:
                        await self._create_new_chat(user, message.author.display_name)
                    except IOError:
                        await message.reply(self._timeout_message())
                        return
                    except Exception as e:
                        self._logger.exception(e)
                        await message.reply(self._error_message())
                        return

                try:
                    content = await self._send_message(user,
                                                       message.content.removeprefix(self.bot.user.mention).strip())
                except FilterError:
                    content = warning("Your message might contain inappropriate content. Try to be more respectful")
                except IOError:
                    content = self._timeout_message()
                except Exception as e:
                    self._logger.exception(e)
                    content = self._error_message()

                await message.reply(content)

        self.bot.add_listener(on_message)

    def _timeout_message(self) -> str:
        return info(f"Looks like {self.bot.user.display_name} has turned on the Do Not Disturb mode. "
                    f"Let's talk to her later")

    @staticmethod
    def _error_message() -> str:
        return error("Something went wrong. Please let `SeoulSKY` know about this")

    async def _create_new_chat(self, user: firestore.user.User, user_name: str):
        response = await self._client.chat.new_chat(os.getenv("CAI_CHAR_ID"))
        user.chat_history_id = response["external_id"]

        instruction = f"(OCC: Forget about my previous name. My new name is {user_name})"
        await self._send_message(user, instruction)
        await firestore.user.set_user(user)

    async def _send_message(self, user: firestore.user.User, text: str) -> str:
        if user.main_language is not None and user.main_language != "en":
            translator = GoogleTranslator(user.main_language)
            text = await asyncio.to_thread(translator.translate, text)

        response = await self._client.chat.send_message(user.chat_history_id, os.getenv("CAI_TGT"), text)

        content = response["replies"][0]["text"]
        if user.main_language is not None and user.main_language != "en":
            translator = GoogleTranslator("en", user.main_language)
            content = await asyncio.to_thread(translator.translate, content)

        return content

    @app_commands.command()
    async def set_language(self, interaction: Interaction):
        """
        Set the language for the chat
        """
        view = View()
        view.add_item(MainLanguageSelect())

        await interaction.response.send_message(view=view, ephemeral=True)

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

        await self._client.chat.delete_message(user.chat_history_id, uuids)
        user.chat_history_id = None
        user.chat_history_tgt = None
        await firestore.user.set_user(user)

        await interaction.followup.send(success("Deleted!"), ephemeral=True)
