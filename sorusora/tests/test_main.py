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

    await bot.login(os.getenv("BOT_TOKEN"))
