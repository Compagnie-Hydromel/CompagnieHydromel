import os
import discord
from dotenv import load_dotenv
from libs.log import Log

load_dotenv()
intents = discord.Intents.all()
archiveuse = discord.Bot(intents=intents)

for filename in os.listdir('./cogs/archiveuse'):
    if filename.endswith('.py'):
        archiveuse.load_extension(f'cogs.archiveuse.{filename[:-3]}')

@archiveuse.event
async def on_ready():
    Log('Archiveuse start with ' + str(archiveuse.user) + ' : ' + str(archiveuse.user.id))


archiveuse.run(os.getenv("ARCHIVEUSE_TOKEN"))