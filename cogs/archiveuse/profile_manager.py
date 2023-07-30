import traceback
import discord

from libs.databases.user import User
from libs.databases.wallpaper import Wallpaper
from libs.databases.wallpapers import Wallpapers
from libs.exception.color_not_correct_exception import ColorNotCorrectException
from libs.exception.not_enougt_smartcoin_exception import NotEnougtSmartcoinException
from libs.exception.wallpaper_already_posseded_exception import WallpaperAlreadyPossededException
from libs.exception.wallpaper_cannot_be_buyed_exception import WallpaperCannotBeBuyedException
from libs.exception.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.exception.wallpaper_not_posseded_exception import WallpaperNotPossededException
from libs.log import Log, LogType
from libs.paginator import Paginator

class ProfileManager(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self._bot = bot

    @discord.slash_command(name="profile-manager", description="To manage your profile")
    @discord.option("option", description="list/change", choices=["set wallpaper", "buy wallpaper", "list of posseded wallpaper", "all wallpaper", "name color", "bar color"])
    @discord.option("text", description="Specifies wallpaper or name and bar color", required=False)
    async def profile_manager(self, ctx: discord.commands.context.ApplicationContext, *, option : str, text : str = None):
        Log(ctx.author.name + " is launching wallpaper commands with " + option + " " + str(text), LogType.COMMAND)
        try:
            await ctx.defer()
            user = User(str(ctx.author.id))
            wallpapers = Wallpapers()

            match option:
                case "set wallpaper":
                    if text == None:
                        text = ""
                    user.change_current_wallpapers(Wallpaper(text))
                    await ctx.respond("Wallpaper changed!")
                case "buy wallpaper":
                    user.buy_wallpaper(Wallpaper(text))
                    await ctx.respond("Wallpaper buyed!")
                case "list of posseded wallpaper":
                    await self.__respond_list_wallpapers(ctx, user.list_of_posseded_wallpapers(), "Posseded wallpapers")
                case "all wallpaper":
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
        except NotEnougtSmartcoinException:
            await ctx.respond("Your not so smart! You don't have enought smartcoin!")
        except WallpaperAlreadyPossededException:
            await ctx.respond("Be smart! Wallpaper already posseded!")
        except WallpaperCannotBeBuyedException:
            await ctx.respond("Be smart! Wallpaper cannot be buyed!")
        except:
            Log(traceback.format_exc(), LogType.ERROR)
            await ctx.respond("An error occured")
            
    async def __respond_list_wallpapers(self, ctx: discord.commands.context.ApplicationContext, wallpapers: list, wallpapers_name: str = "Wallpapers"):
        paginator = Paginator(self.__generate_pages(wallpapers), wallpapers_name)
        
        await ctx.respond(
            view = paginator, 
            embed = paginator.embeb
        )

    def __generate_pages(self, wallpapers: list[Wallpaper]) -> list:
        pages = []
        wallpaper_per_page = 10
        counter = 0
        content = ""
        
        for wallpaper in wallpapers:
            unlock_with = ""
            if wallpaper.price() != 0:
                unlock_with += "\n" + str(wallpaper.price()) + " smartcoin"
            elif wallpaper.level() != 0:
                unlock_with += "\nUnlock at level " + str(wallpaper.level())
            else:
                unlock_with += "\n" + "not buyable"
                
            content += "**" + str(wallpaper.name()) + "**" + unlock_with + "\n"
            counter += 1
            
            if counter > wallpaper_per_page:
                pages.append(content)
                content = ""
                counter = 0
                
        pages.append(content)
        return pages
    
def setup(bot: discord.bot.Bot):
    bot.add_cog(ProfileManager(bot))