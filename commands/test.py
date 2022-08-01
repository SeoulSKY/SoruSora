from discord import app_commands, Interaction


class Parent(app_commands.Group):

    @app_commands.command()
    async def test(self, interaction: Interaction):
        await interaction.response.send_message("This is test")
