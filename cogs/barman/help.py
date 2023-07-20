import  discord

class Help(discord.Cog):
    def __init__(self, bot) -> None:
        self._bot = bot

    @discord.slash_command(name="help", description="List all commands possible")
    async def Help(self, ctx):
        await ctx.respond("WIP!")

def setup(bot):
    bot.add_cog(Help(bot))