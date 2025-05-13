import discord

class SoundboardView (discord.ui.View):
    def __init__ (self, count):
        self.count = count
        super().__init__(timeout=10)
        for i in range(1, count+1): 
            button = discord.ui.Button(style=discord.ButtonStyle.secondary,
                                            label=f"Sound {i}", 
                                            emoji="🎶")
            
            button.callback = self.custom_callback(i)
            self.add_item(button)

    def custom_callback(self, index):
        async def callback (interaction: discord.Interaction):
            await interaction.response.send_message(f"Проигрываю Звук {index} 🎶", ephemeral=True)
        return callback
            

    """@discord.ui.button(label="Sound 1", custom_id="sound_1", style=discord.ButtonStyle.secondary, emoji="🎶")
    async def sound_1 (self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Проигрываю Звук 1 🎶", ephemeral=True)

    @discord.ui.button(label="Sound 2", custom_id="sound_2", style=discord.ButtonStyle.primary, emoji="🎶")
    async def sound_2 (self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Проигрываю Звук 2 🎶", ephemeral=True)

    @discord.ui.button(label="Sound 3", custom_id="sound_3", style=discord.ButtonStyle.success, emoji="🎶")
    async def sound_3 (self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Проигрываю Звук 3 🎶", ephemeral=True)
    
    @discord.ui.button(label="Sound 4", custom_id="sound_4", style=discord.ButtonStyle.danger, emoji="🎶")
    async def sound_4 (self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Проигрываю Звук 4 🎶", ephemeral=True)"""

