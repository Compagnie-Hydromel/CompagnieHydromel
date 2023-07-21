import  discord

from libs.databases.user import User

class Smartcoin(discord.Cog):
    def __init__(self, bot) -> None:
        self._bot = bot

    async def __smartcoin(self, ctx):
        user = User(str(ctx.author.id))

        await ctx.respond("Smartcoin : " + str(user.get_smartcoin()))

    @discord.slash_command(name="smartcoin", description="")
    async def smartcoin(self, ctx):
        await self.__smartcoin(ctx)

    @discord.slash_command(name="iq", description="")
    async def iq(self, ctx):
        await self.__smartcoin(ctx)

def setup(bot):
    bot.add_cog(Smartcoin(bot))