import discord
from libs.config import Config
from libs.log import Log

from libs.databases.model.user.user import User


class Reload(discord.Cog):
    bot: discord.bot.Bot

    def __init__(self, bot):
        self.__bot = bot
        self.__config = Config()
        self.__response_exception = self.__config.value["exception_response"]

    @discord.command(name="reload", help="Reload all cogs")
    async def reload(self, ctx):
        Log.command(ctx.author.name + " is launching reload commands")
        if User(str(ctx.author.id)).is_root:
            extensions = self.__bot.extensions.copy()
            for extension in extensions:
                self.__bot.reload_extension(extension)
            Log.info("Reloaded all cogs from " + str(self.__bot.user))
            await ctx.respond("Reloaded all cogs")
        else:
            await ctx.respond(self.__response_exception["not_root"])


def setup(bot):
    bot.add_cog(Reload(bot))
