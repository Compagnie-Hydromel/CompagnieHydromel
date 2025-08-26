import code
import os
import discord
from dotenv import load_dotenv
from libs.log import Log
import sys
from libs.databases.bootstrap import init
import importlib

bot_name: str

load_dotenv()

if len(sys.argv) < 2:
    Log.info("Starting all bots")
    barman_pid = os.spawnlp(
        os.P_NOWAIT, "python3", "python3", "bot.py", "barman")
    menestrel_pid = os.spawnlp(
        os.P_NOWAIT, "python3", "python3", "bot.py", "menestrel")
    archiveuse_pid = os.spawnlp(
        os.P_NOWAIT, "python3", "python3", "bot.py", "archiveuse")

    os.waitpid(barman_pid, 0)
    os.waitpid(menestrel_pid, 0)
    os.waitpid(archiveuse_pid, 0)
    exit()

init()

match sys.argv[1]:
    case 'barman' | 'menestrel' | 'archiveuse':
        bot_name = sys.argv[1]
    case 'interactive':
        Log.info("Starting interactive mode")
        for filename in os.listdir('./libs/databases/models/'):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = f'libs.databases.models.{filename[:-3]}'
                globals()[filename[:-3]] = importlib.import_module(module_name)
                globals().update({name: getattr(globals()[filename[:-3]], name) for name in dir(
                    globals()[filename[:-3]]) if not name.startswith('_')})
        code.interact(local=globals())
        exit()
    case 'migrate':
        from MIWOS.db import migrate

        migrate()
        Log.info("Migrations completed")
        exit()
    case 'rollback':
        from MIWOS.db import rollback

        rollback(depth=int(sys.argv[2]) if len(sys.argv) > 2 else 1)
        Log.info("Rollback completed")
        exit()
    case 'format':
        from libs.format import PythonFormatter

        formatter = PythonFormatter()
        exit_code = 0
        for file in formatter.format():
            exit_code = 1
            Log.warning(f"Formatted: {file}")
        exit(exit_code)
    case 'check-format':
        from libs.format import PythonFormatter

        formatter = PythonFormatter()
        exit_code = 0
        for file in formatter.check():
            exit_code = 1
            Log.warning(f"Needs formatting: {file}")
        exit(exit_code)
    case 'test':
        test_pid = os.spawnlp(
            os.P_WAIT, "python3", "python3", "-m", "unittest", "discover", "-s", "tests")

        exit(os.WEXITSTATUS(test_pid))
    case _:
        Log.error("Subcommand not found")
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
