from distutils.log import Log
import traceback
import discord
import os

from libs.config import Config
from libs.log import LogType
from libs.utils import Utils

class SexCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self._bot = bot
        self.__config = Config()

    @discord.slash_command(name="porn", description="Get some porn in NSFW channel only")
    @discord.option("choose", description="", choices=["porn", "hentai", "jinx", "002", "overwatch"])
    async def porn(self, ctx: discord.commands.context.ApplicationContext, choose : str):
        try:
            if not ctx.channel.nsfw:
                await ctx.respond("This command can only be used in a NSFW channel")
                return 
            path = self.__config.value["sex_commands"][choose]
            if path != "" and os.path.isdir(path):
                await ctx.respond(file=discord.File(Utils().random_file(path)))
            else:
                await ctx.respond("No porn folder found!")
        except:
            await ctx.respond("An error has occurred, cannot get your porn now please try again later.")
            Log(traceback.format_exc(), LogType.ERROR)

def setup(bot: discord.bot.Bot):
    if Config().value["sex_commands"]["enable"]:
        bot.add_cog(SexCommands(bot))