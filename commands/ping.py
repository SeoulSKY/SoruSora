"""
Implements hello command
"""

import discord
from discord import app_commands
from templates import info


@app_commands.command()
async def ping(interaction: discord.Interaction):
    """Ping this bot"""
    await interaction.response.send_message(info(f'Pong with latency `{interaction.client.latency * 1000}ms`'))
