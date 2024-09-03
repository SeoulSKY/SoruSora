"""
Setup for pytest
"""

import asyncio
import os
import sys

import pytest
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

load_dotenv("..")


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
