import discord
from libs.log import Log

from libs.databases.models.user import User


class Reload(discord.Cog):
    bot: discord.bot.Bot

    def __init__(self, bot):
        self.__bot = bot

    @discord.command(name="reload", help="Reload all cogs")
    async def reload(self, ctx):
        Log.command(ctx.author.name + " is launching reload commands")
        if User.from_discord_id(str(ctx.author.id)).is_superadmin:
            extensions = self.__bot.extensions.copy()
            for extension in extensions:
                self.__bot.reload_extension(extension)
            Log.info("Reloaded all cogs from " + str(self.__bot.user))
            await ctx.respond("Reloaded all cogs")
        else:
            await ctx.respond("You don't have permission to use this command.")


def setup(bot):
    bot.add_cog(Reload(bot))
