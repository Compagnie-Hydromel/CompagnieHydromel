import os
import discord
from dotenv import load_dotenv
from libs.log import Log

load_dotenv()
intents = discord.Intents.all()
menestrel = discord.Bot(intents=intents)

for filename in os.listdir('./cogs/menestrel'):
    if filename.endswith('.py'):
        menestrel.load_extension(f'cogs.menestrel.{filename[:-3]}')

@menestrel.event
async def on_ready():
    Log('Menestrel start with ' + str(menestrel.user) + ' : ' + str(menestrel.user.id))


menestrel.run(os.getenv("MENESTREL_TOKEN"))