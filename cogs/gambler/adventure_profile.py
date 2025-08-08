import discord
from libs.exception.handler import Handler

from libs.log import Log
import traceback

class AdventureProfile(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()

    @discord.slash_command(description="Get your beautiful adventure profile")
    async def adventure_profile(self, ctx: discord.commands.context.ApplicationContext):
        Log.command(ctx.author.name + " is launching adventure_profile commands")
        try:
            await ctx.respond("Salut")



        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

def setup(bot: discord.bot.Bot):
    bot.add_cog(AdventureProfile(bot))
