"""
This module provides functions for channel collection

Classes:
    Channel

Functions:
    has_channel
    get_channel
    set_channel
"""
from dataclasses import dataclass, field

from motor.motor_asyncio import AsyncIOMotorCollection

from mongo import db, Document, has_document, get_document, set_document, get_documents

collection: AsyncIOMotorCollection = db.get_collection("channel")


@dataclass
class Channel(Document):
    """
    A wrapper class to represent channel configs in the database
    """

    channel_id: int = -1
    translate_to: list[str] = field(default_factory=list)
    locale: str = None

    @staticmethod
    def from_dict(source: dict) -> "Channel":
        """
        Create a new channel from the given source
        :param source: The source to create a new channel
        :return: The new channel
        """
        return Document._from_dict(Channel, source)


def _get_filter(channel_id: int) -> dict:
    return {"channel_id": channel_id}


async def has_channel(channel_id: int) -> bool:
    """
    Check if the channel exists in the database
    :param channel_id: The channel id to check
    :return: True if the channel exists, False otherwise
    """

    return await has_document(collection, _get_filter(channel_id))


async def get_channel(channel_id: int) -> Channel:
    """
    Get the channel from the database
    :param channel_id: The channel id to get
    :return: The channel
    """

    doc = await get_document(collection, _get_filter(channel_id))
    if doc is None:
        return Channel(channel_id=channel_id)

    return Channel.from_dict(doc)


async def get_channels(channel_ids: list[int]) -> list[Channel]:
    """
    Get the channels from the database
    :param channel_ids: The channel ids to get
    :return: The channels
    """

    return [Channel.from_dict(channel) for channel in
            await get_documents(collection,{"channel_id": {"$in": channel_ids}})]


async def set_channel(channel: Channel):
    """
    Set the channel to the database
    :param channel: The channel to set
    """
    await set_document(collection, _get_filter(channel.channel_id),  channel.to_dict())
