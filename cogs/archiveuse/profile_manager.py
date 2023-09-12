import traceback
import discord
from libs.config import Config

from libs.databases.user import User
from libs.databases.wallpaper import Wallpaper
from libs.databases.wallpapers import Wallpapers
from libs.exception.color.color_not_correct_exception import ColorNotCorrectException
from libs.exception.smartpoint.not_enougt_smartpoint_exception import NotEnougtsmartpointException
from libs.exception.wallpaper.wallpaper_is_not_downloadable_exception import WallpaperIsNotDownloadableException
from libs.exception.wallpaper.wallpaper_already_posseded_exception import WallpaperAlreadyPossededException
from libs.exception.wallpaper.wallpaper_cannot_be_buyed_exception import WallpaperCannotBeBuyedException
from libs.exception.wallpaper.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper.wallpaper_not_posseded_exception import WallpaperNotPossededException
from libs.log import Log, LogType
from libs.paginator import Paginator
from libs.utils import Utils

class ProfileManager(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config().value

    @discord.slash_command(description="Manage your profile")
    @discord.option("option", description="list/change", choices=["set wallpaper", "buy wallpaper", "list of posseded wallpaper", "all wallpaper", "wallpaper preview", "name color", "bar color"])
    @discord.option("options_specifies", description="Specifies wallpaper or name color and bar color", required=False)
    async def profile_manager(self, ctx: discord.commands.context.ApplicationContext, *, option : str, options_specifies : str = ""):
        Log(ctx.author.name + " is launching wallpaper commands with " + option + " " + str(options_specifies), LogType.COMMAND)
        try:
            await ctx.defer()
            user = User(str(ctx.author.id))
            wallpapers = Wallpapers()

            match option:
                case "set wallpaper":
                    user.change_current_wallpapers(Wallpaper(options_specifies))
                    await ctx.respond(self.__config["response"]["wallpaper_changed"])
                case "buy wallpaper":
                    user.buy_wallpaper(Wallpaper(options_specifies))
                    await ctx.respond(self.__config["response"]["wallpaper_buyed"])
                case "list of posseded wallpaper":
                    await self.__respond_list_wallpapers(ctx, user.list_of_posseded_wallpapers, "Posseded wallpapers")
                case "all wallpaper":
                    await self.__respond_list_wallpapers(ctx, wallpapers.all)
                case "wallpaper preview":
                    await ctx.respond(file=discord.File(Utils().download_image(Wallpaper(options_specifies).url), "wallpaper.png"))
                case "name color":
                    user.change_name_color(options_specifies)
                    await ctx.respond(self.__config["response"]["namecolor_changed"])
                case "bar color":
                    user.change_bar_color(options_specifies)
                    await ctx.respond(self.__config["response"]["namecolor_changed"])
                case _:
                    await ctx.respond(self.__config["exception_response"]["option_not_found"])
        except WallpaperNotExistException:
            await ctx.respond(self.__config["exception_response"]["wallpaper_not_exist"])
        except WallpaperNotPossededException:
            await ctx.respond(self.__config["exception_response"]["wallpaper_not_posseded"])
        except ColorNotCorrectException:
            await ctx.respond(self.__config["exception_response"]["color_not_correct"])
        except NotEnougtsmartpointException:
            await ctx.respond(self.__config["exception_response"]["not_enougt_smartpoint"])
        except WallpaperAlreadyPossededException:
            await ctx.respond(self.__config["exception_response"]["wallpaper_already_posseded"])
        except WallpaperCannotBeBuyedException:
            await ctx.respond(self.__config["exception_response"]["wallpaper_cannot_be_buyed"])
        except WallpaperIsNotDownloadableException:
            await ctx.respond(self.__config["exception_response"]["unable_to_download_image"])
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond(self.__config["exception_response"]["default"])
            
    async def __respond_list_wallpapers(self, ctx: discord.commands.context.ApplicationContext, wallpapers: list, wallpapers_name: str = "Wallpapers"):
        paginator = Paginator(self.__generate_pages(wallpapers), wallpapers_name, 0x75E6DA)
        
        await ctx.respond(
            view = paginator, 
            embed = paginator.embed
        )

    def __generate_pages(self, wallpapers: list[Wallpaper]) -> list:
        pages = []
        wallpaper_per_page = 10
        counter = 0
        content = ""
        
        for wallpaper in wallpapers:
            unlock_with = ""
            if wallpaper.price != 0:
                unlock_with += "\n" + str(wallpaper.price) + " smartpoint"
            elif wallpaper.level != 0:
                unlock_with += "\nUnlock at level " + str(wallpaper.level)
            else:
                unlock_with += "\n" + "not buyable"
                
            content += "**" + str(wallpaper.name) + "**" + unlock_with + "\n"
            counter += 1
            
            if counter > wallpaper_per_page:
                pages.append(content)
                content = ""
                counter = 0
        if content != "":
            pages.append(content)
        return pages
    
def setup(bot: discord.bot.Bot):
    bot.add_cog(ProfileManager(bot))