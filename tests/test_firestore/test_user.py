"""
Test script for configs module
"""

import pytest
from google.cloud.firestore_v1 import Client

from firestore import app, user

db = Client(credentials=app.credential.get_credential(), project=app.project_id)
collection = db.collection("user")
USER_ID = 777


def setup_module():
    """
    Executes before start running any tests
    """
    collection.document(str(USER_ID)).delete()


def teardown_function():
    """
    Executes after every test
    """
    collection.document(str(USER_ID)).delete()


@pytest.mark.asyncio
async def test_has():
    """
    Test has() function
    """
    assert not await user.has_user(USER_ID)

    collection.document(str(USER_ID)).create(user.User(USER_ID).to_dict())

    assert await user.has_user(USER_ID)


@pytest.mark.asyncio
async def test_get_config():
    """
    Test get_config() function
    """
    config = user.User(USER_ID)

    assert (await user.get_user(USER_ID)).to_dict() == config.to_dict()

    config.translate_to = ["en"]
    collection.document(str(USER_ID)).set(config.to_dict())

    assert (await user.get_user(USER_ID)).to_dict() == config.to_dict()


@pytest.mark.asyncio
async def test_set_config():
    """
    Test set_config function
    """
    config = user.User(USER_ID, translate_to=["ko"])

    await user.set_user(config)
    assert collection.document(str(USER_ID)).get().to_dict() == config.to_dict()


if __name__ == "__main__":
    pytest.main()
