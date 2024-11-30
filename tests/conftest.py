"""Setup for pytest."""

import asyncio
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

sys.path.insert(0, str((Path(__file__).parent / "../src").resolve()))
load_dotenv("..")


@pytest.fixture(scope="session")
def event_loop() -> None:
    """Override event loop for async tests."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
