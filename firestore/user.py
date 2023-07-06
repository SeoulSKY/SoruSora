"""
Provides functions to interact with the user configs in the firestore

Classes:
    User

Functions:
    get_collection()
    has_channel()
    get_channel()
    set_channel()
"""

from google.cloud.firestore_v1 import AsyncCollectionReference

from firestore import db


class User:
    """
    A wrapper class to represent user configs in the database
    """

    def __init__(self, user_id: int, chat_history_id: str = None, chat_history_tgt: str = None,
                 translate_to: list[str] = None):
        self.user_id = user_id
        self.chat_history_id = chat_history_id
        self.chat_history_tgt = chat_history_tgt
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
        temp_user_id = 0
        user = User(temp_user_id)
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
    Get the collection of user configs from the database
    :return: The collection of user configs
    """
    return db.collection("user")


async def has_user(user_id: int) -> bool:
    """
    Check if a user has configs in the database
    :param user_id: The user id to check
    :return: True if it does, False otherwise
    """
    return (await get_collection().document(str(user_id)).get()).exists


async def get_user(user_id: int) -> User:
    """
    Get the user configs from the database. If the config is not present, get the default configs
    :param user_id: The user id
    :return: The user configs
    """
    user_doc = await get_collection().document(str(user_id)).get()

    if not user_doc.exists:
        return User(user_id)

    return User.from_dict(user_doc.to_dict())


async def set_user(user: User) -> None:
    """
    Set the user configs in the database
    :param user: The user configs to set
    """
    await get_collection().document(str(user.user_id)).set(user.to_dict())
