import traceback
import discord

from libs.databases.user import User
from libs.exception.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper_not_posseded_exception import WallpaperNotPossededException
from libs.log import Log, LogType

class Wallpaper(discord.Cog):
    def __init__(self, bot) -> None:
        self._bot = bot

    @discord.slash_command(name="wallpaper", description="To change/buy wallpaper")
    @discord.option("option", description="list/change", choices=["Change", "List", "Name Color", "Bar Color"])
    @discord.option("text", description="Wallpaper specified or name and bar color", required=False)
    async def wallpaper(self, ctx, *, option : str, text : str):
        try:
            await ctx.defer()
            user = User(str(ctx.author.id))

            match option:
                case "Change":
                    user.change_current_wallpapers(text)
                    await ctx.respond("Wallpaper changed!")
                case "List":
                    await ctx.respond(embed=self.__generate_embeb(user.list_of_posseded_wallpapers()))
                case "Name Color":
                    user.change_name_color(text)
                    await ctx.respond("Name color changed!")
                case "Bar Color":
                    user.change_bar_color(text)
                    await ctx.respond("Bar color changed!")
                case _:
                    await ctx.respond("Option not found!")
        except WallpaperNotExistException:
            await ctx.respond("Wallpaper not exist!")
        except WallpaperNotPossededException:
            await ctx.respond("Wallpaper not posseded!")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured")

    def __generate_embeb(self, wallpaperList : list) -> discord.Embed:
        description = ""
        
        for i in wallpaperList:
            description += "**" + str(i[0]) + "**\n\n"
        
        return discord.Embed(title="Wallpaper", description=description, color=0x75E6DA)
    
def setup(bot):
    bot.add_cog(Wallpaper(bot))