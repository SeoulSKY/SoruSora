"""
Migrate to v1.1.0
"""

import asyncio
import os
import sys

from deep_translator import GoogleTranslator
from motor.motor_asyncio import AsyncIOMotorCollection
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=wrong-import-position
from src.mongo.user import collection as user_collection
from src.mongo.channel import collection as channel_collection

NAME_TO_CODE = GoogleTranslator().get_supported_languages(as_dict=True)


async def replace_translate_to(collection: AsyncIOMotorCollection):
    """
    Replace the translate_to field with language code
    """
    pbar = tqdm(desc=f"Updating {collection.name} collection", total=await collection.count_documents({}), unit="doc")

    async for doc in collection.find():
        pbar.update(1)
        doc["translate_to"] = [NAME_TO_CODE.get(lang, lang) for lang in doc["translate_to"] if lang in NAME_TO_CODE]
        await collection.replace_one({"_id": doc["_id"]}, doc)

    pbar.close()


async def main():
    """
    Main function
    """
    await replace_translate_to(user_collection)
    await replace_translate_to(channel_collection)

    pbar = tqdm(desc="Updating main_language", total=await user_collection.count_documents({}), unit="doc")
    async for doc in user_collection.find():
        pbar.update(1)
        doc["locale"] = NAME_TO_CODE.get(doc["main_language"], doc["main_language"])
        doc.pop("main_language", None)
        doc.pop("chat_history_tgt", None)
        await user_collection.replace_one({"_id": doc["_id"]}, doc)

    pbar.close()


if __name__ == "__main__":
    asyncio.run(main())
