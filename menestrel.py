import os
import discord
from dotenv import load_dotenv
from libs.log import Log, LogType

load_dotenv()
intents: discord.Intents = discord.Intents.all()
menestrel: discord.bot.Bot = discord.Bot(intents=intents)

for filename in os.listdir('./cogs/menestrel'):
    if filename.endswith('.py'):
        menestrel.load_extension(f'cogs.menestrel.{filename[:-3]}')

@menestrel.event
async def on_ready():
    Log('Menestrel start with ' + str(menestrel.user) + ' : ' + str(menestrel.user.id))

if os.getenv("MENESTREL_TOKEN") is not None:
    menestrel.run(os.getenv("MENESTREL_TOKEN"))
else:
    Log("MENESTREL_TOKEN is not defined in .env file", LogType.ERROR)