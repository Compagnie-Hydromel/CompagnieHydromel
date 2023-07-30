import discord

class Help(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self._bot = bot

    @discord.slash_command(name="help", description="List all commands possible")
    async def help(self, ctx: discord.commands.context.ApplicationContext):
        await ctx.respond("WIP!")

def setup(bot: discord.bot.Bot):
    bot.add_cog(Help(bot))