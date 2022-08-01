from importlib import import_module
import logging
import os
import sys
from inspect import getmembers, isfunction

import discord
from discord import app_commands

TEST_GUILD = discord.Object(id=1003140794217144413)


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

        self._add_commands()

    def _add_commands(self):
        package_name = "commands"

        for module_name in os.listdir(package_name):
            if module_name == "__init__.py" or not module_name.endswith(".py"):
                continue

            module = import_module("." + module_name.removesuffix(".py"), package_name)

            for fn_name, fn in getmembers(module, isfunction):
                if fn_name == "setup":
                    fn(self)

        for group_command_class in app_commands.Group.__subclasses__():
            self.tree.add_command(group_command_class())

    async def setup_hook(self):
        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)


client = MyClient(intents=discord.Intents.all())


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


if __name__ == "__main__":
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    if "BOT_TOKEN" not in os.environ.keys():
        logger.fatal(f"Please set an environment variable \"BOT_TOKEN\" with a Discord Bot's token.")
        sys.exit(1)

    client.run(os.environ.get("BOT_TOKEN"))
