from discord import app_commands, Interaction
from discord.ext.commands import Bot

from firestore import configs


class Translator(app_commands.Group):

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @app_commands.command()
    async def toggle(self, interaction: Interaction):
        """
        Toggle translator for your account
        """

        if not configs.have(interaction.user.id):
            config = configs.Config(interaction.user.id, True)
        else:
            config = configs.get(interaction.user.id)
            config.is_translator_on = not config.is_translator_on

        configs.set(config)
        toggle_value = "on" if config.is_translator_on else "off"
        await interaction.response.send_message(f"Translator has been set to `{toggle_value}`", ephemeral=True)
