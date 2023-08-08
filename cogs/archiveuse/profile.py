import discord
from libs.databases.user import User
from libs.exception.unable_to_download_wallpaper_exception import UnableToDownloadImageException

from libs.log import Log
from libs.profile_maker import ProfilMaker
from libs.utils import Utils
from libs.log import LogType
import traceback

class Profile(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot

    @discord.slash_command(description="To get your beautiful profile")
    async def profile(self, ctx: discord.commands.context.ApplicationContext):
        Log(ctx.author.name + " is launching profile commands", LogType.COMMAND)
        try: 
            await ctx.defer()

            user = User(str(ctx.author.id))

            #coords = {
            #    'profilPicture': {'x': 186, 'y': 35},
            #    'name': {'x': 186, 'y': 155},
            #    'userName': {'x': 190, 'y': 195},
            #    'level': {'x': 250, 'y': 224},
            #    'badge': {'x': 150, 'y': 5},
            #    'levelBar': {'x': 0, 'y': 254}
            #}

            Utils().createDirectoryIfNotExist(".profile")
            pro = ProfilMaker(
                ".profile/" +str(ctx.author.id) + ".png",
                ctx.author.name,
                ctx.author.display_avatar.url,
                user.level(),
                user.point(),
                ctx.author.display_name,
                user.current_wallpaper().url(),
                bar_color = "#"+user.bar_color(),
                name_color = "#"+user.name_color(),
                badges = user.badges_list(),
                #coords = coords
            )

            await ctx.respond(file=discord.File(pro.profil_path()))
            Log(ctx.author.name + " profile saved at " + pro.profil_path(), LogType.INFO)
        except UnableToDownloadImageException:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("Impossible to download image")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured while making profile") 

def setup(bot: discord.bot.Bot):
    bot.add_cog(Profile(bot))
