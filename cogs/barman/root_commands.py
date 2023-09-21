import traceback
import discord
import requests
from libs.config import Config
from libs.databases.user import User
from libs.databases.users import Users
from libs.databases.wallpaper import Wallpaper
from libs.databases.wallpapers import Wallpapers
from libs.exception.color.color_not_correct_exception import ColorNotCorrectException
from libs.exception.handler import Handler
from libs.exception.wallpaper.wallpaper_already_exist_exception import WallpaperAlreadyExistException
from libs.exception.wallpaper.wallpaper_not_exist_exception import WallpaperNotExistException
from libs.log import Log, LogType
from libs.paginator import Paginator
from libs.utils import Utils

class RootCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()
        self.__response = self.__config.value["response"]
        self.__response_exception = self.__config.value["exception_response"]
        self.__error_handler = Handler()
        
    @discord.slash_command(description="Broadcast a message to a any channel as root")
    @discord.option("channel", discord.abc.GuildChannel, require=True)
    @discord.option("message", require=True)
    async def broadcast(self, ctx: discord.commands.context.ApplicationContext, channel: discord.abc.GuildChannel, message: str):
        Log(ctx.author.name + " is launching broadcast commands", LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            if not isinstance(channel, discord.abc.Messageable):
                await ctx.respond(self.__response_exception["channel_not_messageable"])
                return
            
            await channel.send(message.replace("\\n", "\n"))
            await ctx.respond(self.__response["message_sent"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
            
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
                await ctx.respond(self.__response_exception["information_channel_not_found"])
                return
            if not isinstance(information_channel, discord.abc.Messageable):
                await ctx.respond(self.__response_exception["information_channel_not_messageable"])
                return
            
            # WARNING: eval = evil 
            # we check it before to avoid security issue
            embed = discord.Embed(title=title, description=message.replace("\\n", "\n"), color=eval("0x" + Utils().check_color(color)))
            
            await information_channel.send(embed=embed)
            await ctx.respond(self.__response["message_sent"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
            
    @discord.slash_command(description="Clear message in a channel as root")
    async def clear(self, ctx: discord.commands.context.ApplicationContext):
        Log(ctx.author.name + " is launching clear commands", LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            await ctx.respond(self.__response["clearing_channel"])
            await ctx.channel.purge()
            await ctx.channel.send(self.__response["channel_cleared"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
    
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
                    users = Users().get_root_users
                    paginator = Paginator(self.__generate_pages(users), "Root users", 0x75E6DA)
                    
                    await ctx.respond(
                        view = paginator, 
                        embed = paginator.embed
                    )
                case "add":
                    User(str(user.id)).toggle_root(root=True)
                    await ctx.respond(self.__response["user_added_to_root"])
                case "remove":
                    User(str(user.id)).toggle_root(root=False)
                    await ctx.respond(self.__response["user_removed_to_root"])
                case _:
                    await ctx.respond(self.__response_exception["option_not_found"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
    
    @discord.slash_command(description="Send a message to a user as root")
    @discord.option("user", discord.User, require=True)
    @discord.option("message", require=True)
    async def message_user(self, ctx: discord.commands.context.ApplicationContext, user: discord.User, message: str):
        Log(ctx.author.name + " is launching send commands", LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            if not isinstance(user, discord.abc.Messageable):
                await ctx.respond(self.__response_exception["user_not_messageable"])
                return
            
            await user.send(message.replace("\\n", "\n"))
            await ctx.respond(self.__response["message_sent"])
        except discord.Forbidden:
            await ctx.respond(self.__response_exception["cannot_send_message_to_this_user"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
    
    @discord.slash_command(description="Manage smartpoint as root")
    @discord.option("option", description="add/remove/show", choices=["add", "remove", "show"])
    @discord.option("user", discord.User, require=True)
    @discord.option("amount", int, require=False)
    async def manage_smartpoint(self, ctx: discord.commands.context.ApplicationContext, option: str, user: discord.User, amount: int = 0):
        Log(ctx.author.name + " is launching manage smartpoint commands with " + option, LogType.COMMAND)
        try:
            if not await self.__check_if_root(ctx):
                return
            
            user_in_db = User(str(user.id))
            
            match option:
                case "show":
                    await ctx.respond(user.display_name + " smartpoint: " + str(user_in_db.smartpoint))
                case "add" | "remove":
                    if amount < 1:
                        await ctx.respond(self.__response_exception["enter_amount"])
                        return
                    if option == "add":
                        user_in_db.add_smartpoint(amount)
                        await ctx.respond(self.__response["smartpoint_added"])
                    else:
                        user_in_db.remove_smartpoint(amount)
                        await ctx.respond(self.__response["smartpoint_removed"])
                case _:
                    await ctx.respond(self.__response_exception["option_not_found"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

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
                    await ctx.respond("**Name** " + wallpaper.name + 
                                      "\n**url** " + wallpaper.url + 
                                      "\n**price** " + str(wallpaper.price) + " smartpoint" + 
                                      "\n**level to obtain** " + str(wallpaper.level))
                case "add":
                    if not self.__is_url_image(url):
                        await ctx.respond(self.__response_exception["url_not_an_image"])
                        return
                    wallpapers.add(wallpaper_name, url, price, level)
                    await ctx.respond(self.__response["wallpaper_added"])
                case "remove":
                    wallpapers.remove(Wallpaper(wallpaper_name))
                    await ctx.respond(self.__response["wallpaper_removed"])
                case _:
                    await ctx.respond(self.__response_exception["option_not_found"])
        except requests.exceptions.MissingSchema:
            await ctx.respond(self.__response_exception["url_not_good_formated"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
        
    async def __check_if_root(self, ctx: discord.commands.context.ApplicationContext) -> bool:
        if not User(str(ctx.author.id)).is_root:
            await ctx.respond(self.__response_exception["not_root"])
            return False
        return True
    
    def __generate_pages(self, users: list[User]) -> list[str]:
        pages = []
        user_per_page = 10
        counter = 0
        content = ""
        
        for user in users:
            discord_user = self.__bot.get_user(int(user.discord_id))
            if discord_user == None:
                content += "**" + user.discord_id + "**\n"
            else:
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