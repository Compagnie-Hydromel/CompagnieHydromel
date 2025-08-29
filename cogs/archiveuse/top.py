import traceback
import discord

from libs.databases.models.guild import Guild
from libs.exception.handler import Handler
from libs.log import Log
from libs.utils.utils import Utils


class Top(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()

    @discord.slash_command(description="Get the top level up player")
    @discord.option(name="type", description="choose the top", choices=["most active", "smartpoint", "monthly active"], required=False)
    async def top(self, ctx: discord.commands.context.ApplicationContext, type: str = "most active"):
        Log.command(ctx.author.name + " is launching top commands")
        try:
            if not ctx.guild:
                return await ctx.respond("Command can only be used in a server.")

            match type:
                case "smartpoint":
                    await self.__smartpoint(ctx)
                case "monthly active":
                    await self.__monthly_active(ctx)
                case _:
                    await self.__most_active(ctx)

        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    async def __most_active(self, ctx: discord.commands.context.ApplicationContext):
        guild = Guild.from_discord_id(ctx.guild.id)
        list_of_best_users = guild.get_top_users()
        message = ""
        for user in list_of_best_users:
            username = self.__get_user_name_or_id_by_discord_id(
                user.user.discord_id)

            message += f"**{username}** is level {user.level}\n\n"

        await ctx.respond(embed=discord.Embed(title="Top 10 of most active player", description=message, color=0x75E6DA))

    async def __smartpoint(self, ctx: discord.commands.context.ApplicationContext):
        guild = Guild.from_discord_id(ctx.guild.id)
        list_of_best_users = guild.get_most_smart_users()
        message = ""
        for user in list_of_best_users:
            username = self.__get_user_name_or_id_by_discord_id(
                user.user.discord_id)

            message += f"**{username}** has {user.smartpoint} smartpoint\n\n"

        await ctx.respond(embed=discord.Embed(title="Top 10 of player with the most smartpoint", description=message, color=0x75E6DA))

    async def __monthly_active(self, ctx: discord.commands.context.ApplicationContext):
        guild = Guild.from_discord_id(ctx.guild.id)
        list_of_best_users = guild.get_monthly_top_users()
        message = ""
        for user in list_of_best_users:
            username = self.__get_user_name_or_id_by_discord_id(
                user.user.discord_id)

            message += f"**{username}** has {user.monthly_point} monthly point\n\n"

        await ctx.respond(embed=discord.Embed(title="Top 10 most active player of the month", description=message, color=0x75E6DA))

    def __get_user_name_or_id_by_discord_id(self, discord_id: str) -> str:
        return Utils.get_user_name_or_id_by_discord_id(discord_id, self.__bot)


def setup(bot: discord.bot.Bot):
    bot.add_cog(Top(bot))
