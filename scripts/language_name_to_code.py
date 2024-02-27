"""
Replace the translate_to field with language code in MongoDB
"""

import asyncio
import os
import sys

from deep_translator import GoogleTranslator
from motor.motor_asyncio import AsyncIOMotorCollection
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=wrong-import-position
from mongo.user import collection as user_collection
from mongo.channel import collection as channel_collection

NAME_TO_CODE = GoogleTranslator().get_supported_languages(as_dict=True)


async def replace(collection: AsyncIOMotorCollection):
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
    await replace(user_collection)
    await replace(channel_collection)


if __name__ == "__main__":
    asyncio.run(main())
