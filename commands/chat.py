"""
Implements a commands relate to AI chat
"""

import logging
import os

from characterai import PyAsyncCAI
from discord import app_commands, Message, Interaction
from discord.app_commands import Choice
from discord.ext.commands import Bot

from mongo.user import User, get_user, set_user
from utils import defer_response
from utils.constants import languages, BOT_NAME, BUG_REPORT_URL
from utils.templates import info, success, error
from utils.translator import Language, Localization, DEFAULT_LANGUAGE, get_translator

resources = [os.path.join("commands", "chat.ftl"), Localization.get_resource()]
default_loc = Localization(DEFAULT_LANGUAGE, resources)


class Chat(app_commands.Group):
    """
    Commands related to AI chats
    """

    def __init__(self, bot: Bot):
        super().__init__(name=default_loc.format_value("chat-name"),
                         description=default_loc.format_value("chat-description"))
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
                        await message.reply(await self._timeout_message())
                        return
                    except RuntimeError as ex:
                        self._logger.exception(ex)
                        await message.reply(await self._error_message())
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

    async def _timeout_message(self) -> str:
        return info(
            await default_loc.format_value_or_translate("timeout", {"name": self.bot.user.display_name})
        )

    @staticmethod
    async def _error_message() -> str:
        return error(await default_loc.format_value_or_translate("error", {"link": BUG_REPORT_URL}))

    async def _create_new_chat(self, user: User, user_name: str):
        response = await self._client.chat.new_chat(os.getenv("CAI_CHAR_ID"))
        user.chat_history_id = response["external_id"]

        instruction = f"(OCC: Forget about my previous name. My new name is {user_name})"
        await self._send_message(user, instruction)
        await set_user(user)

    async def _send_message(self, user: User, text: str) -> str:
        language = Language(user.locale if user.locale is not None else DEFAULT_LANGUAGE.code)

        response = await self._client.chat.send_message(user.chat_history_id, os.getenv("CAI_TGT"), text)

        content = response["replies"][0]["text"]
        if language != DEFAULT_LANGUAGE:
            content = (await get_translator().translate(content, language)).text

        return content

    @app_commands.command(name=default_loc.format_value("set-language-name"),
                          description=default_loc.format_value("set-language-description"))
    @app_commands.choices(language=[Choice(name=default_loc.format_value(code), value=code) for code in languages])
    @app_commands.describe(language=default_loc.format_value("set-language-language-description"))
    async def set_language(self, interaction: Interaction, language: str = None):
        """
        Set the chat language to the current discord language
        """
        send = await defer_response(interaction)

        user = await get_user(interaction.user.id)
        user.locale = language if language is not None else str(interaction.locale)
        await set_user(user)

        loc = Localization(interaction.locale, resources)

        await send(await loc.format_value_or_translate("updated", {"language": loc.language.name}),
                   ephemeral=True)

    @app_commands.command(name=default_loc.format_value("clear-name"),
                          description=default_loc.format_value("clear-description",
                                                               {"clear-description-name": BOT_NAME}))
    async def clear(self, interaction: Interaction):
        """
        Clear the chat history between you and this bot
        """
        loc = Localization(interaction.locale, resources)

        user = await get_user(interaction.user.id)
        if user.chat_history_id is None:
            await interaction.response.send_message(
                error(await loc.format_value_or_translate("no-history",
                                                    {"name": interaction.client.user.display_name})),
                ephemeral=True)
            return

        await interaction.response.defer()

        response: dict = await self._client.chat.get_history(user.chat_history_id)

        uuids = []
        for message in response["messages"]:
            uuids.append(message["uuid"])

        await self._client.chat.delete_message(user.chat_history_id, uuids)
        user.chat_history_id = None
        user.chat_history_tgt = None
        await set_user(user)

        await interaction.followup.send(success(await loc.format_value_or_translate("deleted")), ephemeral=True)

    clear.extras["clear-description-name"] = BOT_NAME
