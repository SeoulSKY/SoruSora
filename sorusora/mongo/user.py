"""
This module provides functions for user collection

Classes:
    User

Functions:
    has_user
    get_user
    set_user
"""

from motor.motor_asyncio import AsyncIOMotorCollection

from mongo import db, Document, has_document, get_document, set_document

collection: AsyncIOMotorCollection = db.get_collection("user")


class User(Document):
    """
    A wrapper class to represent user in the database
    """
    # pylint: disable=too-many-arguments

    def __init__(self, user_id: int = -1,
                 chat_history_id: str = None,
                 translate_to: list[str] = None,
                 translate_in: list[int] = None,
                 locale: str = None):
        self.user_id = user_id
        self.chat_history_id = chat_history_id
        self.translate_to: list[str] = translate_to if translate_to is not None else []
        self.translate_in: list[str] = translate_in if translate_in is not None else []
        self.locale = locale

    @staticmethod
    def from_dict(source: dict) -> "User":
        """
        Create a new user configs from the given source
        :param source: The source to create a new user
        :return: The new user config
        """
        return Document._from_dict(User, source)


def _get_filter(user_id: int) -> dict:
    return {"user_id": user_id}


async def has_user(user_id: int) -> bool:
    """
    Check if the user exists in the database
    :param user_id: The user id to check
    :return: True if the user exists, False otherwise
    """

    return await has_document(collection, _get_filter(user_id))


async def get_user(user_id: int) -> User:
    """
    Get the user from the database
    :param user_id: The user id to get
    :return: The user
    """

    if not await has_user(user_id):
        return User(user_id)

    return User.from_dict(await get_document(collection, _get_filter(user_id)))


async def set_user(user: User) -> None:
    """
    Update the user in the database. If the user is not present, create a new user
    :param user: The user to update
    """

    await set_document(collection, _get_filter(user.user_id), user.to_dict())
