import traceback
import discord
from libs.config import Config
from libs.databases.model.profile_layout.profile_layout import ProfileLayout
from libs.databases.model.profile_layout.profile_layouts import ProfileLayouts

from libs.databases.model.user.user import User
from libs.databases.model.wallpaper.wallpaper import Wallpaper
from libs.databases.model.wallpaper.wallpapers import Wallpapers
from libs.exception.color.color_not_correct_exception import ColorNotCorrectException
from libs.exception.handler import Handler
from libs.exception.smartpoint.not_enougt_smartpoint_exception import NotEnougtSmartpointException
from libs.exception.wallpaper.wallpaper_is_not_downloadable_exception import WallpaperIsNotDownloadableException
from libs.exception.wallpaper.wallpaper_already_posseded_exception import WallpaperAlreadyPossededException
from libs.exception.wallpaper.wallpaper_cannot_be_buyed_exception import WallpaperCannotBeBuyedException
from libs.exception.wallpaper.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper.wallpaper_not_posseded_exception import WallpaperNotPossededException
from libs.log import Log
from libs.paginator import Paginator
from libs.utils import Utils

class ProfileManager(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()
        self.__response = self.__config.value["response"]
        self.__response_exception = self.__config.value["exception_response"]
        self.__error_handler = Handler()

    @discord.slash_command(description="Manage your profile")
    @discord.option("option", description="list/change", choices=["set wallpaper", "buy wallpaper", "list of posseded wallpaper", "all wallpaper", "wallpaper preview", "name color", "bar color", "list profile layout", "change profile layout"])
    @discord.option("options_specifies", description="Specifies wallpaper or name color and bar color", required=False)
    async def profile_manager(self, ctx: discord.commands.context.ApplicationContext, *, option : str, options_specifies : str = ""):
        Log.command(ctx.author.name + " is launching wallpaper commands with " + option + " " + str(options_specifies))
        try:
            await ctx.defer()
            user = User(str(ctx.author.id))
            wallpapers = Wallpapers()
            profile_layouts = ProfileLayouts()

            match option:
                case "set wallpaper":
                    user.change_current_wallpapers(Wallpaper(options_specifies))
                    await ctx.respond(self.__response["wallpaper_changed"])
                case "buy wallpaper":
                    user.buy_wallpaper(Wallpaper(options_specifies))
                    await ctx.respond(self.__response["wallpaper_buyed"])
                case "list of posseded wallpaper":
                    await self.__respond_list(ctx, user.list_of_posseded_wallpapers, "Posseded wallpapers")
                case "all wallpaper":
                    await self.__respond_list(ctx, wallpapers.all)
                case "wallpaper preview":
                    await ctx.respond(file=discord.File(Utils.download_image(Wallpaper(options_specifies).url), "wallpaper.png"))
                case "name color":
                    user.change_name_color(options_specifies)
                    await ctx.respond(self.__response["namecolor_changed"])
                case "bar color":
                    user.change_bar_color(options_specifies)
                    await ctx.respond(self.__response["namecolor_changed"])
                case "list profile layout":
                    await self.__respond_list(ctx, profile_layouts.get_all_profile_layouts, "Profile layout")
                case "change profile layout":
                    user.change_profile_layout(ProfileLayout(options_specifies))
                    await ctx.respond(self.__response["profile_layout_changed"])
                case _:
                    await ctx.respond(self.__response_exception["option_not_found"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
            
    async def __respond_list(self, ctx: discord.commands.context.ApplicationContext, list: list, page_name: str = "Wallpapers"):
        paginator = Paginator(self.__generate_pages(list), page_name, 0x75E6DA)
        
        await ctx.respond(
            view = paginator, 
            embed = paginator.embed
        )

    def __generate_pages(self, list_of_line: list[any]) -> list:
        pages = []
        line_per_page = 10
        counter = 0
        content = ""
        
        for line in list_of_line:
            if isinstance(line, Wallpaper):
                content += self.wallpaper_list_with_price(line)
            elif isinstance(line, ProfileLayout):
                content += line.name + "\n"
            counter += 1
            
            if counter > line_per_page:
                pages.append(content)
                content = ""
                counter = 0
        if content != "":
            pages.append(content)
        return pages
    
    def wallpaper_list_with_price(self, wallpaper: Wallpaper):
        unlock_with = ""
        if wallpaper.price != 0:
            unlock_with += "\n" + str(wallpaper.price) + " smartpoint"
        elif wallpaper.level != 0:
            unlock_with += "\nUnlock at level " + str(wallpaper.level)
        else:
            unlock_with += "\n" + "not buyable"
            
        return "**" + str(wallpaper.name) + "**" + unlock_with + "\n"
    
def setup(bot: discord.bot.Bot):
    bot.add_cog(ProfileManager(bot))