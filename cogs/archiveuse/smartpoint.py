import traceback
import discord
from libs.config import Config

from libs.databases.model.user.user import User
from libs.exception.handler import Handler
from libs.log import Log


class smartpoint(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()

    async def __smartpoint(self, ctx: discord.commands.context.ApplicationContext):
        Log.command(ctx.author.name + " is launching smartpoint commands")
        try:
            user = User(str(ctx.author.id))

            await ctx.respond("smartpoint : " + str(user.smartpoint))
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Get your number of smartpoint")
    async def smartpoint(self, ctx: discord.commands.context.ApplicationContext):
        await self.__smartpoint(ctx)

    @discord.slash_command(description="Get your number of smartpoint")
    async def iq(self, ctx: discord.commands.context.ApplicationContext):
        await self.__smartpoint(ctx)


def setup(bot: discord.bot.Bot):
    bot.add_cog(smartpoint(bot))
