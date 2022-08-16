from google.cloud.firestore_v1 import AsyncCollectionReference

from firestore import db


class Config:
    """
    A wrapper class to represent user configs in the database
    """

    def __init__(self, user_id: int, is_translator_on: bool = False, translate_to: list[str] = None):
        self.user_id = user_id
        self.is_translator_on = is_translator_on
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
        config = Config(temp_id)
        for key, value in source.items():
            setattr(config, key, value)

        return config

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
    return db.collection("configs")


async def have(user_id: int) -> bool:
    """
    Check if a user has configs in the database
    :param user_id: The user id to check
    :return: True if it does, False otherwise
    """
    return (await get_collection().document(str(user_id)).get()).exists


async def get(user_id: int) -> Config:
    """
    Get the user configs from the database. If the config is not present, get the default configs
    :param user_id: The user id
    :return: The user configs
    """
    user_doc = await get_collection().document(str(user_id)).get()

    if not user_doc.exists:
        return Config(user_id)

    return Config.from_dict(user_doc.to_dict())


async def set(config: Config) -> None:
    """
    Set the user configs in the database
    :param config: The user configs to set
    """
    await get_collection().document(str(config.user_id)).set(config.to_dict())
