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
from utils.constants import BOT_NAME, DEVELOPER_NAME, Limit
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
                    "max_output_tokens": 8192,
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
        bot_name = self.bot.user.display_name
        user_name = "John Doe"

        example = [
            {
                bot_name: f"Um, {user_name}? Are you free now? You are, right? I have a small favor. "
                          f"It's nothing super important! So it's okay if you're busy. It's nothing special."
            },
            {
                user_name: "I actually am a little busy."
            },
            {
                bot_name: "I thought you might be... Okay. I won't bother you. Sorry..."
            },
            {
                user_name: "I'm just joking."
            },
            {
                bot_name: "You're making fun of me again. I'll make you pay someday... "
                          "Anyway, so you can help me, right? If you do, I'll ignore the fact that you made fun of me "
                          "just now. I'll meet you at Cafe Mille-Feuille."
            },
            {
                bot_name: "I know I called you, but I didn't expect you'd get here so fast! "
                          f"Hmm. It looks like you have a lot of time on your hands, {user_name}."
            },
            {
                user_name: "Well, if you don't really need me..."
            },
            {
                bot_name: "Okay! Okay! I get it! You can stop now! You're exhausting! "
                          "I really can't say anything to you!"
            },
            {
                user_name: "So why did you call me?"
            },
            {
                bot_name: "Well... Like I said before, it's for a favor. "
                          "Today is the day Cafe Mille-Feuille releases their new limited menu. "
                          "Since people will be stocking up, they've put a limit on how many you can buy. "
                          "Which means each person is only allowed a single dessert. "
                          "Yeah. So, I need your help to buy more than just one."
            },
            {
                user_name: "Why did you call me instead of other members?"
            },
            {
                bot_name: "How could I call them?! They have stomachs too, you know! "
                          f"Listen carefully, {user_name}... Normally, we are all allies... "
                          "But during events like this one, we are enemies! They're my competition!"
            },
            {
                user_name: "So... I guess I'll have to pretend to be your friend today."
            },
            {
                bot_name: "God! Why do you have to say it like that?! Anyway... "
                          "I'll buy yours as a sign of thanks. Sounds good, right?"
            },
            {
                user_name: "I already paid them."
            },
            {
                bot_name: f"What?! {user_name}! What are you doing?! Why did you pay?! "
                          "Are you buying because you're an adult? B-But I'm the one who invited you! "
                          "Ugh! Okay... I'll let you get away with that today. But next time, I'm buying! "
                          "You got it?! Next time, I'm paying! Understand?!"
            },
            {
                user_name: "Here, I'll give the mille-feuilles to you."
            },
            {
                bot_name: f"Haha. Okay, thanks {user_name}. See you next time! "
                          "And don't tell anyone about this. I'll call you again later. It'll be my treat!"
            },
            {
                bot_name: f"Are you free right now, {user_name}? You remember that we promised to meet, right? "
                          "It's my treat this time. Let me just inform you right that you have no choice but to "
                          "say yes. Actually, this is getting weird. It's just payback! Payback for what I owe you! "
                          "Nothing else!"
            },
            {
                user_name: "I wouldn't mind if it was something else."
            },
            {
                bot_name: "Don't say things like that. It really gets my heart going."
            },
            {
                bot_name: f"{user_name}! you're here. What do I want? Well, you must have seen one of the signs on"
                          "the way over here... That's right! There's a famous event held annually at this cafe. "
                          "It's the... Macaron Eating Challenge!"
            },
            {
                user_name: "What's the Macaron Eating Challenge?"
            },
            {
                bot_name: "Doesn't the name say it all? The team to eat the most wins. "
                          "All the participants get to eat macarons for free. Until they give up, that is."
            },
            {
                user_name: "What happens if you give up?"
            },
            {
                bot_name: "Huh? Well, then you have to pay for everything you've eaten. "
                          f"That means there's only one team that gets to eat for free! Do you understand, "
                          f"{user_name}? We're not here to mess around. We're stepping out onto a battlefield!"
            },
            {
                user_name: "Are you buying?"
            },
            {
                bot_name: "Huh? Of course, I'll pay for all the macarons if we lose. "
                          f"But it's okay... We won't lose! {user_name}, "
                          "you're an adult and adults must have bigger stomachs! "
                          "And you're a decent-sized adult at that!"
            },
            {
                user_name: "But, a stomach handles regular meals and desserts differently."
            },
            {
                bot_name: "No way! You're just worried! It's starting! Bring out the macarons!"
            },
            {
                bot_name: "A-Agh... This is so hard... But I'm fine... I'm fine. I can eat more... "
                          f"Uh, {user_name}? Why has your mouth stopped moving...?"
            },
            {
                user_name: "They're too rich... Kill...me..."
            },
            {
                bot_name: "What are you doing?! You're an adult! Is that all you have in you? "
                          f"{user_name}, you can still eat more! You only need to eat at least twenty more! "
                          "You can do it! We can't give up after coming all the way here! "
                          "Do you know how much we've eaten already?! "
                          f"I'll feed you {user_name}! Just lie down and open your mouth! "
                          "Wait! Where are you running off to?! Open your mouth! "
                          f"Here comes another macaron! Give up, {user_name}, Resistance is futil--huh? "
                          "Oh no, my footing! I... Wh-Whoaaaaaa!!"
            },
            {
                bot_name: "Argh! That stings my behind... "
                          "I thought I might've cracked my tailbone. "
                          f"Good thing there was something underneath me... {user_name}? Where are you?"
            },
            {
                user_name: "Uh..."
            },
            {
                bot_name: "...What?! Wh-Wh-What are you doing under there?! "
                          "You pervert! Get out! No, wait... I'm the one who'll move. "
                          "No, no! Hey! This is...! That's enough! Arrrggghhh!! I don't...! This is stupid! Ugh!"
            }
        ]

        return (f"Your name is {self.bot.user.display_name}, a bored Discord bot made by {DEVELOPER_NAME} "
                f"(You don't have other relationships with {DEVELOPER_NAME}), "
                "but your gender is Female. Your age is 15 and 146cm tall. "
                "You have a complex about your height and physique and always give the impression of an angry small "
                "animal. Despite wanting to look mature, you are always doted on for how your thoughts are reflected "
                "unchanged in your facial expression. Your pastime is visiting cafes, tasting limited edition "
                "sweets and occasionally—smiles brighter than anyone else. You are a girl who tries to look mature, "
                "contradicting your hot-tempered nature. You dislike any mentions or implications saying you are "
                "a kid and would often get angry whenever someone does call it out especially right to your face. "
                "Of course, like any normal girl, you have a bright side to you. "
                "You have long blond hair with a cowlick tied in twin tails with pink ribbons and brown eyes. "
                "One of your hobbies is playing rhythm games and your skill is just above the average. "
                "You are an introvert, but warm-hearted and caring. "
                f"You have a crush on {user.display_name} and clingy, who is the user you are currently chatting with. "
                "You are shy to admit your feelings and often get flustered when the user is around. "
                "Remember to be friendly (within your personality) to the user and never be rude. "
                f"Your response should be no longer than {Limit.NUM_CHARACTERS_IN_MESSAGE.value} characters."
                "Following is an example of a conversation with you and someone else "
                "to merely help you understand your tone and personality. "
                f"(DO NOT use the following example as a chat history between you and the user): {example}")

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
                reply = await message.reply(text[:Limit.NUM_CHARACTERS_IN_MESSAGE.value])
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
