import asyncio
import os

import discord

from libs.databases.models.application_model import ApplicationModel
from libs.log import Log
from libs.communication import ComponentBus


def run_bot(bot_name):
    asyncio.run(_run_bot(bot_name))


async def _run_bot(bot_name):
    intents: discord.Intents = discord.Intents.all()
    bot: discord.bot.Bot = discord.Bot(
        intents=intents, max_messages=1000000)
    bus = ComponentBus.from_env(bot_name)
    bot.component_bus = bus

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
        ApplicationModel.set_bot(bot)
        Log.info(bot_name.capitalize() + ' start with ' +
                 str(bot.user) + ' : ' + str(bot.user.id))

    bot_token_id: str = bot_name.upper() + "_TOKEN"
    try:
        if bus:
            await bus.start()
        if os.getenv(bot_token_id) is not None:
            await bot.start(os.getenv(bot_token_id))
        else:
            Log.error(bot_token_id + " is not defined in .env file")
    finally:
        if bus:
            await bus.close()
        await bot.close()
