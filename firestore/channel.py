"""
Provides functions to interact with the channel configs in the firestore

Functions:
    get_collection()
    has_channel()
    get_channel()
    set_channel()
"""

from google.cloud.firestore_v1 import AsyncCollectionReference

from firestore import db
from mongo.channel import Channel


def get_collection() -> AsyncCollectionReference:
    """
    Get the collection of channel configs from the database
    :return: The collection of channel configs
    """
    return db.collection("channel")


async def has_channel(channel_id: int) -> bool:
    """
    Check if a channel has configs in the database
    :param channel_id: The channel id to check
    :return: True if it does, False otherwise
    """
    return (await get_collection().document(str(channel_id)).get()).exists


async def get_channel(channel_id: int) -> Channel:
    """
    Get the channel configs from the database. If the config is not present, get the default configs
    :param channel_id: The channel id
    :return: The user configs
    """
    channel_doc = await get_collection().document(str(channel_id)).get()

    if not channel_doc.exists:
        return Channel(channel_id)

    return Channel.from_dict(channel_doc.to_dict())


async def set_channel(channel: Channel) -> None:
    """
    Set the channel configs in the database
    :param channel: The channel configs to set
    """
    await get_collection().document(str(channel.channel_id)).set(channel.to_dict())
