"""
Provides functions to interact with the server configs in the firestore

Classes:
    Server

Functions:
    get_collection()
    has_server()
    get_server()
    set_server()
"""

from google.cloud.firestore_v1 import AsyncCollectionReference

from firestore import db


class Server:
    """
    A wrapper class to represent server configs in the database
    """

    def __init__(self, server_id: int, translating_channel_ids: list[int] = None):
        self.server_id = server_id
        if translating_channel_ids is None:
            translating_channel_ids = []
        self.translating_channels_ids = translating_channel_ids

    @staticmethod
    def from_dict(source: dict):
        """
        Create a new server configs from the given source
        :param source: The source to create a new user
        :return: The new server config
        """
        temp_id = 0
        server = Server(temp_id)
        for key, value in source.items():
            setattr(server, key, value)

        return server

    def to_dict(self) -> dict:
        """
        Convert this server configs to dictionary
        :return: The dictionary
        """
        return vars(self)


def get_collection() -> AsyncCollectionReference:
    """
    Get the collection of server configs from the database
    :return: The collection of server configs
    """
    return db.collection("server")


async def has_server(server_id: int) -> bool:
    """
    Check if a server has configs in the database
    :param server_id: The server id to check
    :return: True if it does, False otherwise
    """
    return (await get_collection().document(str(server_id)).get()).exists


async def get_server(server_id: int) -> Server:
    """
    Get the server configs from the database. If the config is not present, get the default configs
    :param server_id: The server id
    :return: The server configs
    """
    user_doc = await get_collection().document(str(server_id)).get()

    if not user_doc.exists:
        return Server(server_id)

    return Server.from_dict(user_doc.to_dict())


async def set_server(server: Server) -> None:
    """
    Set the server configs in the database
    :param server: The server configs to set
    """
    await get_collection().document(str(server.server_id)).set(server.to_dict())
