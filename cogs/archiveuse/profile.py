import discord
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.profile_layout import ProfileLayout
from libs.databases.models.wallpaper import Wallpaper
from libs.exception.handler import Handler

from libs.log import Log
from libs.image_factory.profile_maker import ProfilMaker
from libs.utils.utils import Utils
import traceback


class Profile(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()

    @discord.slash_command(description="Get your beautiful profile")
    async def profile(self, ctx: discord.commands.context.ApplicationContext):
        Log.command(ctx.author.name + " is launching profile commands")
        try:
            await ctx.defer()
            if not ctx.guild:
                return await ctx.respond("Command can only be used in a server.")

            user = GuildUser.from_user_discord_id_and_guild_discord_id(
                ctx.author.id, ctx.guild.id)

            Log.info("create profile for " + str(ctx.author))
            wallpaper = user.wallpaper or Wallpaper.default()
            bar_color = "#" + user.bar_color
            name_color = "#" + user.name_color
            pro = ProfilMaker(
                ctx.author.id,
                ctx.author.name,
                ctx.author.display_avatar.url,
                user.level,
                user.point,
                ctx.author.display_name,
                wallpaper.url,
                bar_color=bar_color,
                name_color=name_color,
                badges=user.user.badges,
                coords=(user.profileLayout or ProfileLayout.default()
                        ).layout.dict(),
                gif=Utils.is_url_animated_gif(wallpaper.url)
            )
            Log.info(ctx.author.name + " profile saved at " + pro.profil_path)

            await ctx.respond(file=discord.File(pro.profil_path))
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))


def setup(bot: discord.bot.Bot):
    bot.add_cog(Profile(bot))
