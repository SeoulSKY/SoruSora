"""
This module provides functions for chat collection

Classes:
    Chat

Functions:
    get_chat
    set_chat
"""

from dataclasses import dataclass, field

from motor.motor_asyncio import AsyncIOMotorCollection

from mongo import db, Document, get_document, set_document

collection: AsyncIOMotorCollection = db.get_collection("chat")


@dataclass
class Message:
    """
    A data class that has information to retrieve a message
    """

    message_id: int
    channel_id: int


@dataclass
class Chat(Document):
    """
    A wrapper class to represent chat in the database
    """

    user_id: int = -1
    history: list[Message] = field(default_factory=list)
    token: bytes = None

    @staticmethod
    def from_dict(source: dict) -> "Chat":
        """
        Create a new chat configs from the given source
        :param source: The source to create a new chat
        :return: The new chat config
        """
        return Document._from_dict(Chat, source)


def _get_filter(user_id: int) -> dict:
    return {"user_id": user_id}


async def get_chat(user_id: int) -> Chat:
    """
    Get the chat of the user from the database

    :param user_id: The user id to get the chat
    """

    doc = await get_document(collection, _get_filter(user_id))
    if doc is None:
        return Chat(user_id=user_id)

    doc["history"] = [Message(**message) for message in doc["history"]]

    return Chat.from_dict(doc)


async def set_chat(chat: Chat) -> None:
    """
    Set the chat of the user in the database

    :param chat: The chat to set
    """
    await set_document(collection, _get_filter(chat.user_id), chat.to_dict())
