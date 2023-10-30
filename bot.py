import os
import discord
from dotenv import load_dotenv
from libs.log import Log, LogType
import sys

bot_name: str

load_dotenv()

if len(sys.argv) < 2:
    Log("Use python3 bot.py <bot_name>", LogType.ERROR)
    exit()

match sys.argv[1]:
    case 'archiveuse':
        bot_name = 'archiveuse'
    case 'menestrel':
        bot_name = 'menestrel'
    case 'barman':
        bot_name = 'barman'
    case _:
        Log("Bot name not found", LogType.ERROR)
        exit()

intents: discord.Intents = discord.Intents.all()
bot: discord.bot.Bot = discord.Bot(intents=intents)

for filename in os.listdir('./cogs/' + bot_name):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{bot_name}.{filename[:-3]}')

@bot.event
async def on_ready():
    Log(bot_name.capitalize() + ' start with ' + str(bot.user) + ' : ' + str(bot.user.id))

bot_token_id: str = bot_name.upper() + "_TOKEN"
if os.getenv(bot_token_id) is not None:
    bot.run(os.getenv(bot_token_id))
else:
    Log(bot_token_id + " is not defined in .env file", LogType.ERROR)