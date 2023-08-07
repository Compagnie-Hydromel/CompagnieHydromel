import traceback
import  discord

from libs.databases.user import User
from libs.log import Log, LogType

class Smartcoin(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot

    async def __smartcoin(self, ctx: discord.commands.context.ApplicationContext):
        Log(ctx.author.name + " is launching smartcoin commands", LogType.COMMAND)
        try:
            user = User(str(ctx.author.id))

            await ctx.respond("Smartcoin : " + str(user.get_smartcoin()))
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured while getting your smartcoin level")

    @discord.slash_command(description="To get your number of smartcoin")
    async def smartcoin(self, ctx: discord.commands.context.ApplicationContext):
        await self.__smartcoin(ctx)

    @discord.slash_command(description="To get your number of smartcoin")
    async def iq(self, ctx: discord.commands.context.ApplicationContext):
        await self.__smartcoin(ctx)

def setup(bot: discord.bot.Bot):
    bot.add_cog(Smartcoin(bot))