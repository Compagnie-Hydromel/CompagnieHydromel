import os
import discord
from dotenv import load_dotenv
from libs.log import Log

load_dotenv()
intents: discord.Intents = discord.Intents.all()
barman: discord.bot.Bot = discord.Bot(intents=intents)

for filename in os.listdir('./cogs/barman'):
    if filename.endswith('.py'):
        barman.load_extension(f'cogs.barman.{filename[:-3]}')

@barman.event
async def on_ready():
    Log('Barman start with ' + str(barman.user) + ' : ' + str(barman.user.id))

barman.run(os.getenv("BARMAN_TOKEN"))