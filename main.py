import discord
from discord.ext import commands
from discord import app_commands
from cryptography.fernet import Fernet
import sqlite3
import os

# ================= ENCRYPTION =================

ENCRYPTION_KEY = b'dLmYrr0fTZ5ESH7RGoAYmfv14rn2JaflOdWgmdKbdzA='
cipher = Fernet(ENCRYPTION_KEY)

# ================= DATABASE =================

conn = sqlite3.connect("callsigns.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS callsigns (
    user_id INTEGER PRIMARY KEY,
    callsign BLOB
)
""")

conn.commit()

# ================= ENV VARS =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

# ================= BOT CLASS =================

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

        try:
            guild = discord.Object(id=GUILD_ID)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to guild {guild.id}')
        except Exception as e:
            print(f'Error syncing commands: {e}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.lower().startswith('afk'):
            await message.channel.send(f'Cya later, {message.author}')

    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        await reaction.message.channel.send('You reacted!')

# ================= BOT SETUP =================

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="?", intents=intents)

# ================= SLASH COMMAND =================

@client.tree.command(
    name="setcs",
    description="Set your callsign.",
    guild=discord.Object(id=GUILD_ID)
)
async def setcs(interaction: discord.Interaction, callsign: str):

    member = interaction.user

    # Check whitelist role
    has_role = any(role.id == WL_ID for role in member.roles)

    if not has_role:
        await interaction.response.send_message(
            "❌ You are not whitelisted to set a callsign.",
            ephemeral=True
        )
        return

    # Enforce minimum length (no admin bypass anymore)
    if len(callsign) < 4:
        await interaction.response.send_message(
            "❌ Callsign must be at least 4 characters long.",
            ephemeral=True
        )
        return

    # Encrypt callsign
    encrypted_callsign = cipher.encrypt(callsign.encode())

    # Insert or update database
    cursor.execute("""
    INSERT INTO callsigns (user_id, callsign)
    VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET callsign=excluded.callsign
    """, (member.id, encrypted_callsign))

    conn.commit()

    await interaction.response.send_message(
        f"✅ Your callsign has been set to **{callsign}**",
        ephemeral=True
    )

    # Send log message
    log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)

    if log_channel:
        await log_channel.send(
            f"{member.name}/<@{member.id}> just changed their callsign to **{callsign}**"
        )

# ================= RUN =================

client.run(BOT_TOKEN)
