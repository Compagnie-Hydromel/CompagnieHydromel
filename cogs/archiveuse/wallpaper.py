import traceback
import discord

from libs.databases.user import User
from libs.databases.wallpapers import Wallpapers
from libs.exception.color_not_correct_exception import ColorNotCorrectException
from libs.exception.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper_not_posseded_exception import WallpaperNotPossededException
from libs.log import Log, LogType
from libs.paginator import Paginator

class Wallpaper(discord.Cog):
    def __init__(self, bot) -> None:
        self._bot = bot

    @discord.slash_command(name="wallpaper", description="To change/buy wallpaper")
    @discord.option("option", description="list/change", choices=["change", "list", "all", "name color", "bar color"])
    @discord.option("text", description="Wallpaper specified or name and bar color", required=False)
    async def wallpaper(self, ctx, *, option : str, text : str = None):
        Log(ctx.author.name + " is launching wallpaper commands with " + option + " " + str(text), LogType.COMMAND)
        try:
            await ctx.defer()
            user = User(str(ctx.author.id))
            wallpapers = Wallpapers()

            match option:
                case "change":
                    user.change_current_wallpapers(text)
                    await ctx.respond("Wallpaper changed!")
                case "list":
                    await self.__respond_list_wallpapers(ctx, user.list_of_posseded_wallpapers(), "Posseded wallpapers")
                case "all":
                    await self.__respond_list_wallpapers(ctx, wallpapers.all())
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
            
    async def __respond_list_wallpapers(self, ctx, wallpapers: list, wallpapers_name: str = "Wallpapers"):
        paginator = Paginator(self.__generate_pages(wallpapers), wallpapers_name)
        
        await ctx.respond(
            view = paginator, 
            embed = paginator.embeb
        )

    def __generate_pages(self, wallpapers: list) -> list:
        pages = []
        wallpaper_per_page = 10
        counter = 0
        content = ""
        
        for wallpaper in wallpapers:
            content = "**" + str(wallpaper[0]) + "**\n\n"
            counter += 1
            
            pages.append(content)
            if counter == wallpaper_per_page:
                content = ""
                counter = 0
        
        return pages
    
def setup(bot):
    bot.add_cog(Wallpaper(bot))