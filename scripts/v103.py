"""Copies all the data from Firestore to MongoDB."""

import asyncio
import sys
from pathlib import Path

import firebase_admin
from firebase_admin import credentials
from google.cloud.firestore_v1 import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.constants import DATABASE_NAME


async def main() -> None:
    """Run the main function."""
    if len(sys.argv) != 3:  # noqa: PLR2004
        sys.exit(1)

    app = firebase_admin.initialize_app(credentials.Certificate(sys.argv[1]))
    firestore = AsyncClient(
        credentials=app.credential.get_credential(), project=app.project_id
    )

    mongo = AsyncIOMotorClient(host=sys.argv[2]).get_database(DATABASE_NAME)

    async for firestore_collection in firestore.collections():
        docs = [doc.to_dict() async for doc in firestore_collection.stream()]

        await mongo.get_collection(firestore_collection.id).insert_many(docs)


if __name__ == "__main__":
    asyncio.run(main())
