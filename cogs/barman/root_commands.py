import traceback
import discord
import requests
from libs.config import Config
from libs.databases.user import User
from libs.databases.users import Users
from libs.databases.wallpaper import Wallpaper
from libs.databases.wallpapers import Wallpapers
from libs.exception.color_not_correct_exception import ColorNotCorrectException
from libs.exception.wallpaper_already_exist_exception import WallpaperAlreadyExistException
from libs.exception.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.log import Log, LogType
from libs.paginator import Paginator
from libs.utils import Utils

class RootCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()

    @discord.slash_command(description="Broadcast a message to a any channel as root")
    @discord.option("channel", discord.abc.GuildChannel, require=True)
    @discord.option("message", require=True)
    async def broadcast(self, ctx: discord.commands.context.ApplicationContext, channel: discord.abc.GuildChannel, message: str):
        Log(ctx.author.name + " is launching broadcast commands", LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            if not isinstance(channel, discord.abc.Messageable):
                await ctx.respond("This channel is not messageable!")
                return
            
            await channel.send(message.replace("\\n", "\n"))
            await ctx.respond("Message sent!")
        except:
            await ctx.respond("An error has occurred, cannot send message now.")
            Log(traceback.format_exc(), LogType.ERROR)
            
    @discord.slash_command(description="Send informations in information channel as root")
    @discord.option("message", require=True)
    @discord.option("title", require=False)
    @discord.option("color", require=False)
    async def info(self, ctx: discord.commands.context.ApplicationContext, message: str, title: str = "Information", color: str = "#ffffff"):
        Log(ctx.author.name + " is launching info commands", LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            information_channel = self.__bot.get_channel(self.__config.value["information_channel_id"])
            if information_channel == None:
                await ctx.respond("Information channel not found! please add it in config.yml")
                return
            if not isinstance(information_channel, discord.abc.Messageable):
                await ctx.respond("The information channel is not messageable! please change it in config.yml")
                return
            
            # WARNING: eval = evil 
            # we check it before to avoid security issue
            embed = discord.Embed(title=title, description=message.replace("\\n", "\n"), color=eval("0x" + Utils().check_color(color)))
            
            await information_channel.send(embed=embed)
            await ctx.respond("Message sent!")
        except ColorNotCorrectException:
            await ctx.respond("The color is not correct! please use hexadecimal color (ex: #ffffff) or use color name (green, blue, red, yellow, orange, pink, black, white, ect...)")
        except:
            await ctx.respond("An error has occurred, cannot send message now.")
            Log(traceback.format_exc(), LogType.ERROR)
            
    @discord.slash_command(description="Clear message in a channel as root")
    async def clear(self, ctx: discord.commands.context.ApplicationContext):
        Log(ctx.author.name + " is launching clear commands", LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            await ctx.respond("Clearing messages...")
            await ctx.channel.purge()
            await ctx.channel.send("Messages cleared!")
        except:
            await ctx.respond("An error has occurred, cannot clear messages now.")
            Log(traceback.format_exc(), LogType.ERROR)
    
    @discord.slash_command(description="Manage root users as root")
    @discord.option("option", description="list/add/remove", choices=["list", "add", "remove"])
    @discord.option("user", discord.User, require=False)
    async def root(self, ctx: discord.commands.context.ApplicationContext, option: str, user: discord.User = None):
        Log(ctx.author.name + " is launching root commands with " + option, LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            
            match option:
                case "list":
                    users = Users().get_root_users()
                    paginator = Paginator(self.__generate_pages(users), "Root users", 0x75E6DA)
                    
                    await ctx.respond(
                        view = paginator, 
                        embed = paginator.embed
                    )
                case "add":
                    User(str(user.id)).toggle_root(root=True)
                    await ctx.respond("User added to root!")
                case "remove":
                    User(str(user.id)).toggle_root(root=False)
                    await ctx.respond("User removed from root!")
                case _:
                    await ctx.respond("Option not found!")
        except:
            await ctx.respond("An error has occurred, cannot clear messages now.")
            Log(traceback.format_exc(), LogType.ERROR)
    
    @discord.slash_command(description="Send a message to a user as root")
    @discord.option("user", discord.User, require=True)
    @discord.option("message", require=True)
    async def message_user(self, ctx: discord.commands.context.ApplicationContext, user: discord.User, message: str):
        Log(ctx.author.name + " is launching send commands", LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            if not isinstance(user, discord.abc.Messageable):
                await ctx.respond("This user is not messageable!")
                return
            
            await user.send(message.replace("\\n", "\n"))
            await ctx.respond("Message sent!")
        except discord.Forbidden:
            await ctx.respond("Cannot send message to this user!")
        except:
            await ctx.respond("An error has occurred, cannot send message to this user!")
            Log(traceback.format_exc(), LogType.ERROR)
    
    @discord.slash_command(description="Manage smartcoin as root")
    @discord.option("option", description="add/remove/show", choices=["add", "remove", "show"])
    @discord.option("user", discord.User, require=True)
    @discord.option("amount", int, require=False)
    async def manage_smartcoin(self, ctx: discord.commands.context.ApplicationContext, option: str, user: discord.User, amount: int = 0):
        Log(ctx.author.name + " is launching manage smartcoin commands with " + option, LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            
            user_in_db = User(str(user.id))
            
            match option:
                case "show":
                    await ctx.respond(user.display_name + " smartcoin: " + str(user_in_db.get_smartcoin()))
                case "add" | "remove":
                    if amount < 1:
                        await ctx.respond("Please enter an amount!")
                        return
                    if option == "add":
                        user_in_db.add_smartcoin(amount)
                        await ctx.respond("Smartcoin added!")
                    else:
                        user_in_db.remove_smartcoin(amount)
                        await ctx.respond("Smartcoin removed!")
                case _:
                    await ctx.respond("Option not found!")
        except:
            await ctx.respond("An error has occurred! please try again later.")
            Log(traceback.format_exc(), LogType.ERROR)

    @discord.slash_command(description="Manage wallpaper as root")
    @discord.option("option", description="add/remove/show", choices=["add", "remove", "show"])
    @discord.option("wallpaper_name", require=True)
    @discord.option("url", require=False)
    @discord.option("price", int, require=False)
    @discord.option("level", int, require=False)
    async def manage_wallpaper(self, ctx: discord.commands.context.ApplicationContext, option: str, wallpaper_name: str, url: str = "", price: int = 0, level: int = 0):
        Log(ctx.author.name + " is launching manage wallpaper commands with " + option, LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return

            wallpapers = Wallpapers()
            
            match option:
                case "show":
                    wallpaper = Wallpaper(wallpaper_name)
                    await ctx.respond("**Name** " + wallpaper.name() + 
                                      "\n**url** " + wallpaper.url() + 
                                      "\n**price** " + str(wallpaper.price()) + " smartcoin" + 
                                      "\n**level to obtain** " + str(wallpaper.level()))
                case "add":
                    if not self.__is_url_image(url):
                        await ctx.respond("Please make sure url is an image!")
                        return
                    wallpapers.add(wallpaper_name, url, price, level)
                    await ctx.respond("Added!")
                case "remove":
                    wallpapers.remove(Wallpaper(wallpaper_name))
                    await ctx.respond("Removed!")
                case _:
                    await ctx.respond("Option not found!")
        except requests.exceptions.MissingSchema:
            await ctx.respond("Please enter an valid url!")
        except WallpaperAlreadyExistException: 
            await ctx.respond("Wallpaper already exist!")
        except WallpaperNotExistException:
            await ctx.respond("Wallpaper not found!")
        except:
            await ctx.respond("An error has occurred! please try again later.")
            Log(traceback.format_exc(), LogType.ERROR)
        
    async def __check_if_root(self, ctx: discord.commands.context.ApplicationContext) -> bool:
        if not User(str(ctx.author.id)).is_root():
            await ctx.respond("You are not root!")
            return False
        return True
    
    def __generate_pages(self, users: list[User]) -> list[str]:
        pages = []
        user_per_page = 10
        counter = 0
        content = ""
        
        for user in users:
            discord_user = self.__bot.get_user(int(user.discord_id()))
            content += "**" + discord_user.display_name + "**\n"
            counter += 1
            if counter > user_per_page:
                pages.append(content)
                content = ""
                counter = 0
        if content != "":
            pages.append(content)
        return pages
    
    def __is_url_image(self, image_url):
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(image_url)
        if r.headers["content-type"] in image_formats:
            return True
        return False

    
def setup(bot: discord.bot.Bot):
    bot.add_cog(RootCommands(bot))