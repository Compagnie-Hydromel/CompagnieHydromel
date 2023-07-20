import os
import discord
from dotenv import load_dotenv

load_dotenv()
barman = discord.Bot()
menestrel = discord.bot()
archiveuse = discord.bot()

# for filename in os.listdir('./cogs'):
#     if filename.endswith('.py'):
#         bot.load_extension(f'cogs.{filename[:-3]}')

@barman.event
@menestrel.event
@archiveuse.event
async def on_ready():
    print("start")

barman.run(os.getenv("BARMAN_TOKEN"))
menestrel.run(os.getenv("MENESTREL_TOKEN"))
archiveuse.run(os.getenv("ARCHIVEUSE_TOKEN"))