"""
Test script for configs module
"""

import pytest
from google.cloud.firestore_v1 import Client

from firestore import app, configs

db = Client(credentials=app.credential.get_credential(), project=app.project_id)
collection = db.collection("configs")
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
    assert not await configs.has_config(USER_ID)

    collection.document(str(USER_ID)).create(configs.Config(USER_ID).to_dict())

    assert await configs.has_config(USER_ID)


@pytest.mark.asyncio
async def test_get_config():
    """
    Test get_config() function
    """
    config = configs.Config(USER_ID)

    assert (await configs.get_config(USER_ID)).to_dict() == config.to_dict()

    config.translate_to = ["en"]
    collection.document(str(USER_ID)).set(config.to_dict())

    assert (await configs.get_config(USER_ID)).to_dict() == config.to_dict()


@pytest.mark.asyncio
async def test_set_config():
    """
    Test set_config function
    """
    config = configs.Config(USER_ID, translate_to=["ko"])

    await configs.set_config(config)
    assert collection.document(str(USER_ID)).get().to_dict() == config.to_dict()


if __name__ == "__main__":
    pytest.main()
