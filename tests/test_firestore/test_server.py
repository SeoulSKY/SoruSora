"""
Test script for server module
"""

import pytest
from google.cloud.firestore_v1 import Client

from firestore import app, server

db = Client(credentials=app.credential.get_credential(), project=app.project_id)
collection = db.collection("server")
SERVER_ID = 888


def setup_module():
    """
    Executes before start running any tests
    """
    collection.document(str(SERVER_ID)).delete()


def teardown_function():
    """
    Executes after every test
    """
    collection.document(str(SERVER_ID)).delete()


@pytest.mark.asyncio
async def test_has_server():
    """
    Test has_server() function
    """
    assert not await server.has_server(SERVER_ID)

    collection.document(str(SERVER_ID)).create(server.Server(SERVER_ID).to_dict())

    assert await server.has_server(SERVER_ID)


@pytest.mark.asyncio
async def test_get_server():
    """
    Test get_server() function
    """
    config = server.Server(SERVER_ID)

    assert (await server.get_server(SERVER_ID)).to_dict() == config.to_dict()

    config.translating_channels_ids = [14, 55]
    collection.document(str(SERVER_ID)).set(config.to_dict())

    assert (await server.get_server(SERVER_ID)).to_dict() == config.to_dict()


@pytest.mark.asyncio
async def test_set_server():
    """
    Test set_server function
    """
    config = server.Server(SERVER_ID, [7, 13])

    await server.set_server(config)
    assert collection.document(str(SERVER_ID)).get().to_dict() == config.to_dict()


if __name__ == "__main__":
    pytest.main()
