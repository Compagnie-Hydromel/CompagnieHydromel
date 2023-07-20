import  discord

class Play(discord.Cog):
    def __init__(self, bot) -> None:
        self._bot = bot

    @discord.slash_command(name="play", description="")
    async def play(self, ctx):
        await ctx.respond("WIP!")

def setup(bot):
    bot.add_cog(Play(bot))