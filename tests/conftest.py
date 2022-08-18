"""
Setup for pytest
"""

import asyncio

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """
    Override event loop for async tests
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
