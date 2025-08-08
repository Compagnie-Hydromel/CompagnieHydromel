import os
import discord
from dotenv import load_dotenv
from libs.log import Log
import sys

bot_name: str

load_dotenv()

if len(sys.argv) < 2:
    Log.error("Use python3 bot.py <bot_name>")
    exit()

match sys.argv[1]:
    case 'barman' | 'menestrel' | 'archiveuse' | 'gambler':
        bot_name = sys.argv[1]
    case _:
        Log.error("Bot name not found")
        exit()

intents: discord.Intents = discord.Intents.all()
bot: discord.bot.Bot = discord.Bot(intents=intents, max_messages=1000000)

# Load specific bot cogs
for filename in os.listdir('./cogs/' + bot_name):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{bot_name}.{filename[:-3]}')

# Load common cogs
for filename in os.listdir('./cogs/'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_ready():
    Log.info(bot_name.capitalize() + ' start with ' +
             str(bot.user) + ' : ' + str(bot.user.id))

bot_token_id: str = bot_name.upper() + "_TOKEN"
if os.getenv(bot_token_id) is not None:
    bot.run(os.getenv(bot_token_id))
else:
    Log.error(bot_token_id + " is not defined in .env file")
