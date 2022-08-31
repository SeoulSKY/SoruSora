"""
Provides functions to interact with the channel configs in the firestore

Classes:
    Channel

Functions:
    get_collection()
    has_channel()
    get_channel()
    set_channel()
"""

from google.cloud.firestore_v1 import AsyncCollectionReference

from firestore import db


class Channel:
    """
    A wrapper class to represent channel configs in the database
    """

    def __init__(self, channel_id: int, translate_to: list[str] = None):
        self.channel_id = channel_id
        if translate_to is None:
            translate_to = []
        self.translate_to: list[str] = translate_to

    @staticmethod
    def from_dict(source: dict):
        """
        Create a new user configs from the given source
        :param source: The source to create a new user
        :return: The new user config
        """
        temp_id = 0
        user = Channel(temp_id)
        for key, value in source.items():
            setattr(user, key, value)

        return user

    def to_dict(self) -> dict:
        """
        Convert this user configs to dictionary
        :return: The dictionary
        """
        return vars(self)


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
