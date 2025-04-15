import discord
from libs.databases.model.user import User
from libs.exception.handler import Handler
from libs.exception.wallpaper.wallpaper_is_not_downloadable_exception import WallpaperIsNotDownloadableException

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

            user = User(str(ctx.author.id))

            Utils.createDirectoryIfNotExist(".profile")

            output_end = ".png"

            if Utils.is_url_animated_gif(user.current_wallpaper.url):
                output_end = ".gif"

            Log.info("create profile for " + str(ctx.author))
            pro = ProfilMaker(
                ".profile/" + str(ctx.author.id) + output_end,
                ctx.author.name,
                ctx.author.display_avatar.url,
                user.level,
                user.point,
                ctx.author.display_name,
                user.current_wallpaper.url,
                bar_color=user.bar_color,
                name_color=user.name_color,
                badges=user.badges_list,
                coords=user.profiles_layout.layout.dict()
            )
            Log.info(ctx.author.name + " profile saved at " + pro.profil_path)

            await ctx.respond(file=discord.File(pro.profil_path))
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))


def setup(bot: discord.bot.Bot):
    bot.add_cog(Profile(bot))
