"""
This module provides database instances for mongo

Instances:
    db

Classes:
    Collection

Functions:
    has_document
    get_document
    set_document
"""
import os
from typing import Type, TypeVar, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from utils.constants import DATABASE_NAME

client = AsyncIOMotorClient(host="mongo") if os.getenv("DOCKER") else AsyncIOMotorClient()
db: AsyncIOMotorDatabase = client.get_database(DATABASE_NAME)

T = TypeVar("T", bound="Collection")


class Document:  # pylint: disable=too-few-public-methods
    """
    A wrapper class to represent documents in the database
    """

    @staticmethod
    def _from_dict(child_class: Type[T], source: dict) -> T:
        """
        Create a new document from the given source
        :param child_class: The child class of Document
        :param source: The source to create a new user
        :return: The new document
        """

        collection = child_class()
        for key, value in source.items():
            setattr(collection, key, value)

        return collection

    def to_dict(self) -> dict:
        """
        Convert this document to dictionary
        :return: The dictionary
        """
        return vars(self)


async def has_document(collection: AsyncIOMotorCollection, doc_filter: dict) -> bool:
    """
    Check if the document exists in the collection
    :param collection: The target collection
    :param doc_filter: The filter to check
    :return: True if the document exists, False otherwise
    """

    return await collection.count_documents(doc_filter) > 0


async def get_document(collection: AsyncIOMotorCollection, doc_filter: dict) -> Optional[dict]:
    """
    Get the document from the collection
    :param collection: The target collection
    :param doc_filter: The filter to get
    :return: The document, or None if it does not exist
    """

    return await collection.find_one(doc_filter)


async def set_document(collection: AsyncIOMotorCollection, doc_filter: dict, doc: dict) -> None:
    """
    Set the document to the collection. If the document does not exist, it will be created
    :param collection: The target collection
    :param doc_filter: The filter to set
    :param doc: The document to set
    """

    await collection.update_one(doc_filter, {"$set": doc}, upsert=True)
