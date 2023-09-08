import traceback
import  discord
from libs.config import Config

from libs.databases.user import User
from libs.log import Log, LogType

class smartpoint(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config().value

    async def __smartpoint(self, ctx: discord.commands.context.ApplicationContext):
        Log(ctx.author.name + " is launching smartpoint commands", LogType.COMMAND)
        try:
            user = User(str(ctx.author.id))

            await ctx.respond("smartpoint : " + str(user.smartpoint))
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond(self.__config["exception_response"]["default"])

    @discord.slash_command(description="Get your number of smartpoint")
    async def smartpoint(self, ctx: discord.commands.context.ApplicationContext):
        await self.__smartpoint(ctx)

    @discord.slash_command(description="Get your number of smartpoint")
    async def iq(self, ctx: discord.commands.context.ApplicationContext):
        await self.__smartpoint(ctx)

def setup(bot: discord.bot.Bot):
    bot.add_cog(smartpoint(bot))