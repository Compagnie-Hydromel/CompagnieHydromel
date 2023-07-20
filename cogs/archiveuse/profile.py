import  discord
from libs.databases.user import User
from libs.exception.unable_to_download_wallpaper import UnableToDownloadImage

from libs.log import Log
from libs.profile_maker import ProfilMaker
from libs.utils import Utils
from libs.log import LogType
import traceback

class Profile(discord.Cog):
    def __init__(self, bot) -> None:
        self._bot = bot

    @discord.slash_command(name="profile", description="")
    async def profile(self, ctx):
        Log(ctx.author.name + " is lauching profile commands", LogType.COMMAND)
        try: 
            await ctx.defer()

            user = User(str(ctx.author.id))

            Utils().createDirectoryIfNotExist(".profile")
            pro = ProfilMaker(
                ".profile/" +str(ctx.author.id) + ".png",
                ctx.author.name,
                ctx.author.display_avatar.url,
                user.level(),
                user.point(),
                ctx.author.display_name,
                background_url="https://shkermit.ch/~ethann/compHydromelWallpaper/default.png",
            )

            await ctx.respond(file=discord.File(pro.profil_path()))
        except UnableToDownloadImage:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("Impossible to download image")
        except: 
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured while making profile") 

def setup(bot):
    bot.add_cog(Profile(bot))