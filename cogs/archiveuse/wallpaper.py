import traceback
import discord

from libs.databases.user import User
from libs.databases.wallpapers import Wallpapers
from libs.exception.color_not_correct_exception import ColorNotCorrectException
from libs.exception.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper_not_posseded_exception import WallpaperNotPossededException
from libs.log import Log, LogType

class Wallpaper(discord.Cog):
    def __init__(self, bot) -> None:
        self._bot = bot

    @discord.slash_command(name="wallpaper", description="To change/buy wallpaper")
    @discord.option("option", description="list/change", choices=["change", "list", "all", "name color", "bar color"])
    @discord.option("text", description="Wallpaper specified or name and bar color", required=False)
    async def wallpaper(self, ctx, *, option : str, text : str):
        try:
            await ctx.defer()
            user = User(str(ctx.author.id))
            wallpaper = Wallpapers()

            match option:
                case "change":
                    user.change_current_wallpapers(text)
                    await ctx.respond("Wallpaper changed!")
                case "list":
                    await ctx.respond(embed=self.__generate_embeb(user.list_of_posseded_wallpapers(),embeb_name = "Your wallpapers"))
                case "all":
                    await ctx.respond(embed=self.__generate_embeb(wallpaper.all()))
                case "name color":
                    user.change_name_color(text)
                    await ctx.respond("Name color changed!")
                case "bar color":
                    user.change_bar_color(text)
                    await ctx.respond("Bar color changed!")
                case _:
                    await ctx.respond("Option not found!")
        except WallpaperNotExistException:
            await ctx.respond("Wallpaper not exist!")
        except WallpaperNotPossededException:
            await ctx.respond("Wallpaper not posseded!")
        except ColorNotCorrectException:
            await ctx.respond("Color is not correct!")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured")

    def __generate_embeb(self, wallpaper_list: list, embeb_name: str = "Wallpapers") -> discord.Embed:
        description = ""
        
        for i in wallpaper_list:
            description += "**" + str(i[0]) + "**\n\n"
        
        return discord.Embed(title=embeb_name, description=description, color=0x75E6DA)
    
def setup(bot):
    bot.add_cog(Wallpaper(bot))