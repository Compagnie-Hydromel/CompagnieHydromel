import traceback
import  discord
from libs.config import Config

from libs.databases.user import User
from libs.exception.handler import Handler
from libs.log import Log, LogType

class smartpoint(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot

    async def __smartpoint(self, ctx: discord.commands.context.ApplicationContext):
        Log(ctx.author.name + " is launching smartpoint commands", LogType.COMMAND)
        try:
            user = User(str(ctx.author.id))

            await ctx.respond("smartpoint : " + str(user.smartpoint))
        except Exception as e:
            await ctx.respond(Handler().response_handler(e))

    @discord.slash_command(description="Get your number of smartpoint")
    async def smartpoint(self, ctx: discord.commands.context.ApplicationContext):
        await self.__smartpoint(ctx)

    @discord.slash_command(description="Get your number of smartpoint")
    async def iq(self, ctx: discord.commands.context.ApplicationContext):
        await self.__smartpoint(ctx)

def setup(bot: discord.bot.Bot):
    bot.add_cog(smartpoint(bot))