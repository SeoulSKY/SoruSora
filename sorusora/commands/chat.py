"""
Implements a commands relate to AI chat
"""
import asyncio
import logging
import os

import grpc
from discord import app_commands, Message, Interaction
from discord.ext.commands import Bot

from protos import chatAI_pb2
from protos.chatAI_pb2_grpc import ChatAIStub

from mongo.user import User, get_user, set_user
from utils import defer_response
from utils.constants import BOT_NAME
from utils.templates import success, error, unknown_error
from utils.translator import Language, Localization, DEFAULT_LANGUAGE, get_translator
from utils.ui import LanguageSelectView

resources = [os.path.join("commands", "chat.ftl"), Localization.get_resource()]
default_loc = Localization(DEFAULT_LANGUAGE, resources)

CURRENT_LANGUAGE_DEFAULT = True


async def _select_language(interaction: Interaction, language: Language, send: callable):
    user = await get_user(interaction.user.id)
    user.locale = language.code
    await set_user(user)

    loc = Localization(interaction.locale, resources)

    await send(success(await loc.format_value_or_translate("updated", {"language": language.name})),
               ephemeral=True)


class ChatLanguageSelectView(LanguageSelectView):
    """
    A view to select a language for the chat
    """

    def __init__(self, interaction: Interaction):
        loc = Localization(interaction.locale, resources)
        super().__init__(loc.format_value_or_translate("set-language-select"), interaction.locale, max_values=1)

    async def callback(self, interaction: Interaction):
        await super().callback(interaction)

        send = await defer_response(interaction)

        await _select_language(interaction, Language(list(self.selected)[0]), send)

        self.clear_items()
        self.stop()


class Chat(app_commands.Group):
    """
    Commands related to AI chats
    """
    # pylint: disable=no-member

    CHAT_AI_URL = os.getenv("CHAT_AI_HOST", "localhost") + ":" + "50051"

    def __init__(self, bot: Bot):
        super().__init__(name=default_loc.format_value("chat-name"),
                         description=default_loc.format_value("chat-description"))
        self.bot = bot
        self._logger = logging.getLogger(__name__)

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

                try:
                    if user.chat_history_id is None:
                        await self._create_new_chat(user, message.author.display_name)
                        user = await get_user(message.author.id)
                    text = await self._send_message(user,
                                                       message.content.removeprefix(self.bot.user.mention).strip())
                    await message.reply(text)
                except Exception as ex:
                    language = Language(user.locale) if user.locale is not None else DEFAULT_LANGUAGE
                    await message.reply(await unknown_error(language), suppress_embeds=True)
                    raise ex

        self.bot.add_listener(on_message)

    @staticmethod
    async def _create_new_chat(user: User, user_name: str) -> None:
        with grpc.insecure_channel(Chat.CHAT_AI_URL) as channel:
            try:
                response = await asyncio.to_thread(ChatAIStub(channel).Create,
                                                   chatAI_pb2.CreateRequest(name=user_name))
            except Exception as ex:
                raise RuntimeError("Failed to create a new chat") from ex

        user.chat_history_id = response.chatId
        await set_user(user)

    @staticmethod
    async def _send_message(user: User, text: str) -> None:
        with grpc.insecure_channel(Chat.CHAT_AI_URL) as channel:
            try:
                response = await asyncio.to_thread(ChatAIStub(channel).Send,
                                                   chatAI_pb2.SendRequest(chatId=user.chat_history_id, text=text))
            except Exception as ex:
                raise RuntimeError("Failed to send a message to AI") from ex

        language = Language(user.locale) if user.locale is not None else DEFAULT_LANGUAGE
        text = response.text
        if language != DEFAULT_LANGUAGE:
            text = (await get_translator().translate(text, language)).text

        return text

    @app_commands.command(name=default_loc.format_value("set-language-name"),
                          description=default_loc.format_value("set-language-description"))
    @app_commands.describe(
        current_language=default_loc.format_value(
            "set-language-current-language-description",
            {"set-language-current-language-description-default": str(CURRENT_LANGUAGE_DEFAULT)}
        )
    )
    async def set_language(self, interaction: Interaction, current_language: bool = CURRENT_LANGUAGE_DEFAULT):
        """
        Set the chat language to the current discord language
        """
        send = await defer_response(interaction)

        if current_language:
            await _select_language(interaction, Language(interaction.locale), send)
            return

        await send(view=await ChatLanguageSelectView(interaction).init(), ephemeral=True)

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
                error(await loc.format_value_or_translate("no-history",{"name": BOT_NAME})),
                ephemeral=True)
            return

        await interaction.response.defer()

        with grpc.insecure_channel(self.CHAT_AI_URL) as channel:
            stub = ChatAIStub(channel)

            try:
                await asyncio.to_thread(stub.Clear, chatAI_pb2.ClearRequest(chatId=user.chat_history_id))
            except grpc.RpcError as ex:
                if ex.code() == grpc.StatusCode.NOT_FOUND:
                    await interaction.followup.send(
                        error(await loc.format_value_or_translate("no-history",{"name": BOT_NAME})),
                        ephemeral=True)
                    return

                await interaction.followup.send(await unknown_error(interaction.locale), ephemeral=True)
                raise RuntimeError("Failed to clear chat history") from ex

            except Exception as ex:
                await interaction.followup.send(await unknown_error(interaction.locale), ephemeral=True)
                raise RuntimeError("Failed to clear chat history") from ex

        user.chat_history_id = None
        await set_user(user)
        await interaction.followup.send(success(await loc.format_value_or_translate("deleted")), ephemeral=True)

    set_language.extras["set-language-current-language-description-default"] = CURRENT_LANGUAGE_DEFAULT
    clear.extras["clear-description-name"] = BOT_NAME
