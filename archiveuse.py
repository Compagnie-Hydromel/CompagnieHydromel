import os
import discord
from dotenv import load_dotenv
from libs.log import Log, LogType

load_dotenv()
intents: discord.Intents = discord.Intents.all()
archiveuse: discord.bot.Bot = discord.Bot(intents=intents)

for filename in os.listdir('./cogs/archiveuse'):
    if filename.endswith('.py'):
        archiveuse.load_extension(f'cogs.archiveuse.{filename[:-3]}')

@archiveuse.event
async def on_ready():
    Log('Archiveuse start with ' + str(archiveuse.user) + ' : ' + str(archiveuse.user.id))

if os.getenv("ARCHIVEUSE_TOKEN") is not None:
    archiveuse.run(os.getenv("ARCHIVEUSE_TOKEN"))
else:
    Log("ARCHIVEUSE_TOKEN is not defined in .env file", LogType.ERROR)