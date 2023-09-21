from libs.exception.handler import Handler
from libs.log import Log
import traceback
import discord
import os

from libs.config import Config
from libs.log import LogType
from libs.utils import Utils

class NsfwCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()
        self.__config = Config()
        self.__error_exception = self.__config.value["exception_response"]

    @discord.slash_command(description="Get some NSFW content in a NSFW channel")
    @discord.option("choose", description="", choices=["porn", "hentai", "jinx", "002", "overwatch"])
    async def porn(self, ctx: discord.commands.context.ApplicationContext, choose : str):
        Log(ctx.author.name + " is launching sex commands with " + choose, LogType.COMMAND)
        try:
            if not ctx.channel.nsfw:
                await ctx.respond(self.__error_exception["not_nsfw_channel"])
                return 
            path = self.__config.value["nsfw_commands"][choose]
            if path != "" and os.path.isdir(path):
                await ctx.respond(file=discord.File(Utils().random_file(path)))
            else:
                await ctx.respond(self.__error_exception["folder_not_found"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

def setup(bot: discord.bot.Bot):
    if Config().value["nsfw_commands"]["enable"]:
        bot.add_cog(NsfwCommands(bot))