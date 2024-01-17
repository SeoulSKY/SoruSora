"""
Clears all app commands of the bot
"""

import os
import sys

import discord
from discord.ext.commands import Bot
from dotenv import load_dotenv


class TempBot(Bot):
    """
    Temporary bot to clear all commands
    """

    async def setup_hook(self) -> None:
        self.tree.clear_commands(guild=None)
        await self.tree.sync()

        print("Done")
        sys.exit(0)


if __name__ == "__main__":
    load_dotenv()

    bot = TempBot(command_prefix="!", intents=discord.Intents.all())
    bot.run(os.getenv("BOT_TOKEN"))
