import  discord

class Play(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self._bot = bot

    @discord.slash_command(name="play", description="")
    async def play(self, ctx: discord.commands.context.ApplicationContext):
        await ctx.respond(str(type(self._bot)))

def setup(bot: discord.bot.Bot):
    bot.add_cog(Play(bot))