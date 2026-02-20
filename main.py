import discord
from discord.ext import commands
from discord import app_commands

class Client(commands.Bot):
	async def on_ready(self):
		print(f'Logged on as {self.user}!')

		try:
			guild = discord.Object(id=1463577470191140896)
			synced = await self.tree.sync(guild=guild)
			print(f'Synced {len(synced)} command(s) to guild {guild.id}')

		except Exception as e:
			print(f'Error syncing commands: {e}')

	async def on_message(self, message):
		if message.author == self.user:
			return

		if message.content.startswith('AFK') or message.content.startswith('afk'):
					await message.channel.send(f'Cya later, {message.author}')

	async def on_reaction_add(self, reaction, user):
		await reaction.message.channel.send('You reacted!')


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="?", intents=intents)

GUILD_ID = discord.Object(id=1463577470191140896)

@client.tree.command(name="hello", description="Say hello!", guild=GUILD_ID)
async  def sayHello(interaction: discord.Interaction):
	await interaction.response.send_message("Hi there!")


@client.tree.command(name="print", description="Print string.", guild=GUILD_ID)
async  def printer(interaction: discord.Interaction, printer: str):
	await interaction.response.send_message(printer)

@client.tree.command(name="embed", description="Create an embed.", guild=GUILD_ID)
async  def embed(interaction: discord.Interaction, titl: str, desc: str):
	embed = discord.Embed(title=titl, description=desc, color=discord.Colour.brand_green())
	# embed.add_field(name="Field 1 Title", value="Field 1 Value", inline=False)
	# embed.add_field(name="Field 2 Title", value="Field 2 Value", inline=False)
	await interaction.response.send_message(embed=embed)

@client.tree.command(name="server", description="Toggle server status.", guild=GUILD_ID)
async def server_status(interaction: discord.Interaction):
    channel = interaction.guild.get_channel(1463611154889707543)

    if channel is None:
        await interaction.response.send_message("Channel not found.", ephemeral=True)
        return

    if channel.name == "Status-❎":
        await channel.edit(name="Status-✅")
        await interaction.response.send_message("Server is now ONLINE.")
    else:
        await channel.edit(name="Status-❎")
        await interaction.response.send_message("Server is now OFFLINE.")

client.run()


# To start py, do "py main.py"
# To end py, do CTRL+C in terminal
