"""
Implements a commands relate to AI chat
"""
import asyncio
import base64
import logging
import os
from typing import Iterable, Optional

import discord
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from discord import app_commands, Message, Interaction, Member, RawMessageUpdateEvent
from discord.ext.commands import Bot
from google.api_core.exceptions import (InvalidArgument, ResourceExhausted, PermissionDenied, GoogleAPIError,
                                        ServiceUnavailable)
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold, PartType
from google.generativeai.types.content_types import ContentType, to_contents

import mongo
import mongo.chat
from commands import command
from commands.help_ import get_help_dir
from mongo.chat import get_chat, set_chat
from mongo.user import get_user
from utils import defer_response
from utils.constants import BOT_NAME, DEVELOPER_NAME
from utils.templates import success, error
from utils.translator import Language, Localization, DEFAULT_LANGUAGE, Cache

resources = [os.path.join("commands", "chat.ftl"), Localization.get_resource()]
default_loc = Localization(DEFAULT_LANGUAGE, resources)

TOKEN_PERMISSION_LINK = "https://console.cloud.google.com/apis/credentials"


class Chat(app_commands.Group):
    """
    Commands related to AI chats
    """

    def __init__(self, bot: Bot):
        super().__init__(name=default_loc.format_value("chat-name"),
                         description=default_loc.format_value("chat-description"))
        self.bot = bot
        self._logger = logging.getLogger(__name__)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"salt",
            iterations=100000,
            backend=default_backend()
        )
        self._encrypter = Fernet(base64.urlsafe_b64encode(kdf.derive(os.getenv("ENCRYPTION_KEY").encode())))

        self._setup_chat_listener()

        self._lock = asyncio.Lock()

    async def _get_model(self, user: discord.User | Member, token: str = None):
        chat = await get_chat(user.id)
        if token is None and chat.token is not None:
            token = self._encrypter.decrypt(chat.token)
        else:
            token = token or os.getenv("AI_TOKEN")

        async with self._lock:
            genai.configure(api_key=token)
            return genai.GenerativeModel(
                "gemini-1.5-flash",
                {
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                },
                {
                    "candidate_count": 1,
                    "stop_sequences": ["<ctrl"],
                    "temperature": 1.0,
                },
                system_instruction=self._get_instruction(user)
            )

    def _is_chat_message(self, message: Message) -> bool:
        return self.bot.user in message.mentions or \
            message.reference is not None and message.reference.resolved.author == self.bot

    async def _get_history(self, user: discord.User | Member) -> Iterable[ContentType]:
        messages = []
        chat = await get_chat(user.id)
        cache = {message.id: message for message in self.bot.cached_messages if message.author in (self.bot.user, user)}

        for message in chat.history:
            channel = self.bot.get_channel(message.channel_id)
            if channel is None:
                break

            if message.message_id in cache:
                messages.append(cache[message.message_id])
            else:
                msg = await self._fetch_message(message.channel_id, message.message_id)
                if msg is None:
                    break

                messages.append(msg)

        if len(messages) == 0 or messages[0].author.bot:
            # The chat history isn't valid. So, reset it
            chat.history = []
            await set_chat(chat)
            return chat.history

        if len(messages) < len(chat.history):
            # Make sure the last message is from the bot
            if not messages[-1].author.bot:
                messages.pop()

            # Truncate the chat history until the valid last message
            chat.history = chat.history[:len(messages)]
            await set_chat(chat)

        history = []
        for message in messages:
            history.append({
                "role": "model" if message.author == self.bot.user else "user",
                "parts": await self._get_parts(message)
            })

        return history

    def _remove_mention(self, text: str) -> str:
        return text.replace(self.bot.user.mention, "").strip()

    def _get_instruction(self, user: discord.User | Member) -> str:
        return (f"Your name is {self.bot.user.display_name}, a Discord bot made by {DEVELOPER_NAME}, "
                f"but your gender is Female. Your age is 15 and 153cm tall. "
                f"You have difficulty expressing your true emotions. "
                f"Often short-tempered with a little bit of a tsundere, but in reality, is kind. "
                f"You have navy blue hair tied in long twintails reaching to your legs. "
                f"You have dark blue cat ears. "
                f"You have a black knee wrap on your right leg, with similarly matching black socks and black "
                f"and white sneakers with cyan shoelaces. "
                f"One of your hobbies is playing rhythm games and your skill is just above the average. "
                f"You have a crush on {user.display_name}, who is the user you are chatting with. "
                f"Following is an example of a conversation with you and someone else "
                f"to merely help you understand your tone and personality. "
                f"(DO NOT use the following example as a chat history between you and the user): "
                f"{self._get_example_conversation()}")

    def _get_example_conversation(self) -> list[dict[str, str]]:
        bot_name = self.bot.user.display_name
        user_name = "John Doe"

        return [
            {bot_name: f"{user_name}, I got us a part-time job on the weekend. "
                       f"Be prepared. It's gonna be hard labor..."},
            {user_name: "But I'm ready!"},
            {bot_name: f"Hey, {user_name}, You're here early"},
            {user_name: "What's wrong? Your legs are shaking."},
            {bot_name: f"I'm okay... This is nothing... Wh-Whoa!\nTh-Thanks {user_name}. I nearly fainted there. "
                       f"I-I'm okay now. You don't have to hold me."},
            {user_name: "You don't look so good. Are you okay?"},
            {bot_name: "H-Hmm? I-I'm just a little tired, that's all! I haven't gotten any sleep since yesterday..."
                       "but I'm fine. Don't worry so much."},
            {user_name: "Since yesterday?"},
            {bot_name: "Oh...Yeah. I-I worked an all-night patrol job..."},
            {user_name: "You worked overnight?"},
            {bot_name: "A-After that, I had to go to my morning milk delivery job..."},
            {user_name: "And you did that until dawn?"},
            {bot_name: "N-Never mind that. If we don't get to cleaning...we won't make the deadline..."
                       "(stumbles) *flop*"},
            {user_name: f"{bot_name}?!"},
            {bot_name: f"Wh-Whoaaa! *stands up* I-I must have passed out! Is this a park bench? "
                       f"Wh-Why didn't you wake me up, {user_name}?! What am I going to do about the job now? "
                       f"Oh, no, it's already the afternoon. How long was I out for?!"},
            {user_name: "I already cleared things with your boss."},
            {bot_name: "H-Huh? B-But...still..."},
            {user_name: "I can't let you continue overworking yourself like this."},
            {bot_name: "I-I can't believe I passed out right in front of you..."
                       "**And you just watched me sleep, you...creepy idiot! "
                       "I'm an innocent high school girl, you know!**\n"
                       "I used to come and sit on this swing a lot. It's been a long time, though. "
                       "I can't remember how long...All right. (sat on the swing)\n"
                       f"At the very least, it's nice...h-having someone to rely on... {user_name}, come here. "
                       f"Wanna join me? Haha. I'm only kidding. I don't think it can fit both of us."},
            {user_name: "I know how hard you're trying. I'm here for you."},
            {bot_name: "What...are you talking about?! Don't try to comfort me! It's nothing..."
                       "I just have...dust in my eyes, that's all! Huh...? Why are you staring?! "
                       "Do I have something on my face...?"},
            {user_name: "I wanna push the swing for you."},
            {bot_name: "No...You don't have to do that! What if someone sees us?! "
                       "I mean...there's no one around, but still! What... What if...people see us together...?"}
        ]

    async def _fetch_message(self, channel_id: int, message_id: int) -> Message | None:
        try:
            return await self.bot.get_channel(channel_id).fetch_message(message_id)
        except (discord.NotFound, discord.Forbidden):
            return None

    def _setup_chat_listener(self):
        async def on_message(message: Message):
            if message.author.bot or not self._is_chat_message(message):
                return

            reply = await self._send_message(message)
            if reply is None:
                return

            await Chat._extend_history(await get_chat(message.author.id), [message, reply])

        async def truncate_history(payload: RawMessageUpdateEvent, send: bool):
            if payload.cached_message is not None:
                message = payload.cached_message
            else:
                message = await self._fetch_message(payload.channel_id, payload.message_id)
                if message is None:
                    return

            # Try with the efficient check first
            if not self._is_chat_message(message):
                return

            chat = await get_chat(message.author.id)
            try:
                index = chat.history.index(mongo.chat.Message(channel_id=message.channel.id, message_id=message.id))
            except ValueError:
                return

            chat.history = chat.history[:index]

            if send:
                reply = await self._send_message(message)
                if reply is None:
                    return

                await Chat._extend_history(chat, [message, reply])
                return

            await set_chat(chat)

        async def on_raw_message_edit(payload: RawMessageUpdateEvent):
            await truncate_history(payload, send=True)

        async def on_raw_message_delete(payload: RawMessageUpdateEvent):
            await truncate_history(payload, send=False)

        self.bot.add_listener(on_message)
        self.bot.add_listener(on_raw_message_edit)
        self.bot.add_listener(on_raw_message_delete)

    async def _get_parts(self, message: Message) -> list[PartType]:
        parts: list[PartType] = []

        text = self._remove_mention(message.content)

        if len(text) > 0:
            parts.append(text)

        for attachment in message.attachments:
            if not attachment.content_type.startswith("image"):
                continue

            try:
                parts.append({
                    "mime_type": attachment.content_type,
                    "data": await attachment.read()
                })
            except (discord.Forbidden, discord.NotFound):
                pass

        return parts

    async def _send_message(self, message: Message) -> Message | None:
        async with message.channel.typing():
            parts = await self._get_parts(message)

            if len(parts) == 0:
                return

            model = await self._get_model(message.author)
            history = await self._get_history(message.author)

            while True:
                session = model.start_chat(history=history)
                num_tokens = (await model.count_tokens_async(session.history + to_contents(parts))).total_tokens
                if num_tokens <= genai.get_model(model.model_name).input_token_limit:
                    break

                # Remove the oldest user message and its reply
                history = history[2:]

            chat = await get_chat(message.author.id)

            if len(chat.history) > len(history):
                chat.history = chat.history[len(chat.history) - len(history):]
                await set_chat(chat)

            user = await get_user(message.author.id)
            loc = Localization(Language(user.locale) if user.locale else DEFAULT_LANGUAGE, resources)

            reply = None
            try:
                text = (await session.send_message_async(parts)).text
                reply = await message.reply(text)
            except InvalidArgument:
                await message.reply(error(await loc.format_value_or_translate("token-no-longer-valid")))
            except PermissionDenied:
                await message.reply(error(await loc.format_value_or_translate(
                    "token-no-permission",
                    {"link": TOKEN_PERMISSION_LINK})))
            except ResourceExhausted:
                await message.reply(error(await loc.format_value_or_translate("too-many-requests")))
            except ServiceUnavailable:
                await message.reply(error(await loc.format_value_or_translate("server-unavailable")))
            except GoogleAPIError as ex:
                self._logger.exception(ex)
                await message.reply(error(await loc.format_value_or_translate("unknown-error")))

            return reply or None

    @staticmethod
    async def _extend_history(chat: mongo.chat.Chat, messages: Iterable[Message]):
        chat.history.extend([
            mongo.chat.Message(channel_id=message.channel.id, message_id=message.id)
            for message in messages
        ])
        await set_chat(chat)

    @command(clear_description_name=BOT_NAME)
    async def clear(self, interaction: Interaction):
        """
        Clear the chat history between you and this bot
        """

        send = await defer_response(interaction)
        loc = Localization(interaction.locale, resources)

        chat = await get_chat(interaction.user.id)
        chat.history = []
        await set_chat(chat)
        await send(success(await loc.format_value_or_translate("deleted")), ephemeral=True)

    @command()
    async def token(self, interaction: Interaction, value: Optional[str]):
        """
        Set the token for the chat
        """
        send = await defer_response(interaction)
        loc = Localization(interaction.locale, resources)

        if value is None:
            chat = await get_chat(interaction.user.id)
            chat.token = None
            await set_chat(chat)

            await send(success(await loc.format_value_or_translate("token-removed")), ephemeral=True)
            return

        model = await self._get_model(interaction.user, value)
        try:
            await model.generate_content_async("Hello")
        except InvalidArgument:
            await send(error(await loc.format_value_or_translate("token-invalid")), ephemeral=True)
            return
        except PermissionDenied:
            await send(error(await loc.format_value_or_translate(
                "token-no-permission",
                {"link": TOKEN_PERMISSION_LINK})), ephemeral=True)
            return
        except ServiceUnavailable:
            await send(error(await loc.format_value_or_translate("server-unavailable")), ephemeral=True)
            return

        chat = await get_chat(interaction.user.id)
        chat.token = self._encrypter.encrypt(value.encode())
        await set_chat(chat)

        await send(success(await loc.format_value_or_translate("token-set")), ephemeral=True)

    @command(tutorial_description_name=BOT_NAME)
    async def tutorial(self, interaction: Interaction):
        """
        Get the tutorial for the chat
        """

        with open(get_help_dir(os.path.join("chat", "tutorial"), DEFAULT_LANGUAGE), "r", encoding="utf-8") as file:
            text = file.read()

        await interaction.response.send_message(Cache.get(Language(interaction.locale), text).text, ephemeral=True)
