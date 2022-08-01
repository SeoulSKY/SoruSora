import discord
from discord import app_commands

from main import MyClient


@app_commands.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


def setup(client: MyClient):
    client.tree.add_command(hello)
