"""
Test script for user module
"""

import pytest
from google.cloud.firestore_v1 import Client

from firestore import app, channel

db = Client(credentials=app.credential.get_credential(), project=app.project_id)
collection = db.collection("channel")
CHANNEL_ID = 777


def setup_module():
    """
    Executes before start running any tests
    """
    collection.document(str(CHANNEL_ID)).delete()


def teardown_function():
    """
    Executes after every test
    """
    collection.document(str(CHANNEL_ID)).delete()


@pytest.mark.asyncio
async def test_has_channel():
    """
    Test has_channel() function
    """
    assert not await channel.has_channel(CHANNEL_ID)

    collection.document(str(CHANNEL_ID)).create(channel.Channel(CHANNEL_ID).to_dict())

    assert await channel.has_channel(CHANNEL_ID)


@pytest.mark.asyncio
async def test_get_channel():
    """
    Test get_channel() function
    """
    config = channel.Channel(CHANNEL_ID)

    assert (await channel.get_channel(CHANNEL_ID)).to_dict() == config.to_dict()

    config.translate_to = ["en"]
    collection.document(str(CHANNEL_ID)).set(config.to_dict())

    assert (await channel.get_channel(CHANNEL_ID)).to_dict() == config.to_dict()


@pytest.mark.asyncio
async def test_set_channel():
    """
    Test set_channel function
    """
    config = channel.Channel(CHANNEL_ID, translate_to=["ko"])

    await channel.set_channel(config)
    assert collection.document(str(CHANNEL_ID)).get().to_dict() == config.to_dict()


if __name__ == "__main__":
    pytest.main()
