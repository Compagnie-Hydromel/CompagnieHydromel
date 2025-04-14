from libs.exception.handler import Handler
from libs.log import Log
import traceback
import discord
import os

from libs.config import Config
from libs.utils.utils import Utils

config = Config()
choice_list = list(config.value["nsfw_commands"]["nsfw_content"].keys())


class NsfwCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()
        self.__config = Config()
        self.__error_exception = self.__config.value["exception_response"]
        self.__path = self.__config.value["nsfw_commands"]["nsfw_content"]

    @discord.slash_command(description="Get some NSFW content in a NSFW channel")
    @discord.option("choose", description="", choices=choice_list)
    async def porn(self, ctx: discord.commands.context.ApplicationContext, choose: str):
        Log.command(ctx.author.name +
                    " is launching porn commands with " + choose)
        try:
            if not ctx.channel.nsfw:
                await ctx.respond(self.__error_exception["not_nsfw_channel"])
                return

            if self.__path[choose] != "" and os.path.isdir(self.__path[choose]):
                await ctx.respond(file=discord.File(Utils.random_file(self.__path[choose])))
            else:
                await ctx.respond(self.__error_exception["folder_not_found"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))


def setup(bot: discord.bot.Bot):
    if config.value["nsfw_commands"]["enable"]:
        bot.add_cog(NsfwCommands(bot))
