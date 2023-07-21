import discord
from discord.ext import commands
from paginator import Paginator, Page, NavigationType

class PaginatorTest(discord.Cog):
    def __init__(self, bot) -> None:
        self.paginator = Paginator(bot)
        self._bot = bot

    @discord.slash_command(name="paginator", description="Paginator")
    async def paginator(self, ctx):
        pages = [
            Page(content="Click!", embed=discord.Embed(title="Page #1", description="Testing")),
            Page(embed=discord.Embed(title="Page #2", description="Still testing")),
            Page(embed=discord.Embed(title="Page #3", description="Guess... testing"))
        ]

        await self.paginator.send(ctx.channel, pages, type=NavigationType.Buttons)

def setup(bot):
    bot.add_cog(PaginatorTest(bot))