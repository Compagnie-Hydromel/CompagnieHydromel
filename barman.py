import os
import discord
from dotenv import load_dotenv
from libs.log import Log

load_dotenv()
barman = discord.Bot()

for filename in os.listdir('./cogs/barman'):
    if filename.endswith('.py'):
        barman.load_extension(f'cogs.barman.{filename[:-3]}')

@barman.event
async def on_ready():
    Log('Barman start with ' + str(barman.user) + ' : ' + str(barman.user.id))

barman.run(os.getenv("BARMAN_TOKEN"))