import traceback
import discord

from libs.databases.models.guild_user import GuildUser
from libs.exception.handler import Handler
from libs.log import Log


class smartpoint(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()

    async def __smartpoint(self, ctx: discord.commands.context.ApplicationContext):
        Log.command(ctx.author.name + " is launching smartpoint commands")
        try:
            if not ctx.guild:
                return await ctx.respond("Command can only be used in a server.")

            user = GuildUser.from_user_discord_id_and_guild_discord_id(
                str(ctx.author.id), str(ctx.guild.id))

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
