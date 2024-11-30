"""Provides functions for user collection.

Classes:
    User

Functions:
    has_user
    get_user
    set_user
"""

from dataclasses import dataclass, field

from motor.motor_asyncio import AsyncIOMotorCollection

from mongo import Document, db, get_document, has_document, set_document

collection: AsyncIOMotorCollection = db.get_collection("user")


@dataclass
class User(Document):
    """A wrapper class to represent user in the database."""

    user_id: int = -1
    translate_to: list[str] = field(default_factory=list)
    translate_in: list[str] = field(default_factory=list)
    locale: str = None

    @staticmethod
    def from_dict(source: dict) -> "User":
        """Create a new user configs from the given source
        :param source: The source to create a new user
        :return: The new user config.
        """
        return super()._from_dict(User, source)


def _get_filter(user_id: int) -> dict:
    return {"user_id": user_id}


async def has_user(user_id: int) -> bool:
    """Check if the user exists in the database
    :param user_id: The user id to check
    :return: True if the user exists, False otherwise.
    """
    return await has_document(collection, _get_filter(user_id))


async def get_user(user_id: int) -> User:
    """Get the user from the database
    :param user_id: The user id to get
    :return: The user.
    """
    doc = await get_document(collection, _get_filter(user_id))
    if doc is None:
        return User(user_id=user_id)

    return User.from_dict(doc)


async def set_user(user: User) -> None:
    """Update the user in the database. If the user is not present, create a new user
    :param user: The user to update.
    """
    await set_document(collection, _get_filter(user.user_id), user.to_dict())
