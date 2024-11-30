"""Provides database instances for mongo.

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
from collections.abc import Iterator
from dataclasses import asdict, is_dataclass
from typing import TypeVar

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from utils.constants import DATABASE_NAME

client = (
    AsyncIOMotorClient(host="mongo") if os.getenv("DOCKER") else AsyncIOMotorClient()
)
db: AsyncIOMotorDatabase = client.get_database(DATABASE_NAME)

T = TypeVar("T", bound="Document")


class Document:
    """A wrapper class to represent documents in the database."""

    @staticmethod
    def _from_dict(child_class: type[T], source: dict) -> T:
        """Create a new document from the given source
        :param child_class: The child class of Document
        :param source: The source to create a new user
        :return: The new document.
        """
        # Only include keys that are actual attributes of the child class
        valid_keys = set(child_class.__annotations__.keys())
        filtered_source = {k: v for k, v in source.items() if k in valid_keys}

        return child_class(**filtered_source)

    def to_dict(self) -> dict:
        """Convert this document to dictionary
        :return: The dictionary.
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                result[key] = [asdict(v) if is_dataclass(v) else v for v in value]
            elif is_dataclass(value):
                result[key] = asdict(value)
            else:
                result[key] = value

        return result


async def has_document(collection: AsyncIOMotorCollection, doc_filter: dict) -> bool:
    """Check if the document exists in the collection
    :param collection: The target collection
    :param doc_filter: The filter to check
    :return: True if the document exists, False otherwise.
    """
    return await collection.count_documents(doc_filter) > 0


async def get_document(
    collection: AsyncIOMotorCollection, doc_filter: dict
) -> dict | None:
    """Get the document from the collection
    :param collection: The target collection
    :param doc_filter: The filter to get
    :return: The document, or None if it does not exist.
    """
    return await collection.find_one(doc_filter)


async def get_documents(
    collection: AsyncIOMotorCollection, doc_filter: dict
) -> Iterator[dict]:
    """Get the documents from the collection
    :param collection: The target collection
    :param doc_filter: The filter to get
    :return: The documents.
    """
    return await collection.find(doc_filter).to_list(length=None)


async def set_document(
    collection: AsyncIOMotorCollection, doc_filter: dict, doc: dict
) -> None:
    """Set the document to the collection. If the document does not exist,
    it will be created.
    :param collection: The target collection
    :param doc_filter: The filter to set
    :param doc: The document to set.
    """
    await collection.update_one(doc_filter, {"$set": doc}, upsert=True)
