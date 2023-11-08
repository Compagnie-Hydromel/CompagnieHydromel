import discord
from libs.databases.user.user import User
from libs.exception.handler import Handler
from libs.exception.wallpaper.wallpaper_is_not_downloadable_exception import WallpaperIsNotDownloadableException

from libs.log import Log
from libs.profile_maker import ProfilMaker
from libs.utils import Utils
from libs.log import LogType
import traceback

class Profile(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()
        
    @discord.slash_command(description="Get your beautiful profile")
    async def profile(self, ctx: discord.commands.context.ApplicationContext):
        Log(ctx.author.name + " is launching profile commands", LogType.COMMAND)
        try: 
            await ctx.defer()

            user = User(str(ctx.author.id))

            Utils().createDirectoryIfNotExist(".profile")
            pro = ProfilMaker(
                ".profile/" +str(ctx.author.id) + ".png",
                ctx.author.name,
                ctx.author.display_avatar.url,
                user.level,
                user.point,
                ctx.author.display_name,
                user.current_wallpaper.url,
                bar_color = user.bar_color,
                name_color = user.name_color,
                badges = user.badges_list,
                coords = user.profiles_layout.layout.dict()
            )

            await ctx.respond(file=discord.File(pro.profil_path))
            Log(ctx.author.name + " profile saved at " + pro.profil_path, LogType.INFO)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

def setup(bot: discord.bot.Bot):
    bot.add_cog(Profile(bot))
