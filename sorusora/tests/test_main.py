"""
Contains tests for main.py
"""
import os

import pytest

from main import bot


@pytest.mark.asyncio
async def test_setup_hook():
    """
    Test setup_hook() of the bot
    """

    token = os.getenv("BOT_TOKEN")
    assert token is not None and len(token) != 0

    await bot.login(token)
