import traceback
import discord
import requests
from libs.config import Config
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout
from libs.databases.model.profile_layout.profile_layout import ProfileLayout
from libs.databases.model.profile_layout.profile_layouts import ProfileLayouts
from libs.databases.model.roles.role import Role
from libs.databases.model.roles.roles import Roles
from libs.databases.model.user.user import User
from libs.databases.model.user.users import Users
from libs.databases.model.wallpaper.wallpaper import Wallpaper
from libs.databases.model.wallpaper.wallpapers import Wallpapers
from libs.exception.handler import Handler
from libs.log import Log
from libs.paginator import Paginator
from libs.utils.utils import Utils
from libs.utils.role_utils import RoleUtils

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
        Log.command(ctx.author.name + " is launching broadcast commands")
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
        Log.command(ctx.author.name + " is launching info commands")
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
            embed = discord.Embed(title=title, description=message.replace("\\n", "\n"), color=eval("0x" + Utils.check_color(color)))
            
            await information_channel.send(embed=embed)
            await ctx.respond(self.__response["message_sent"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
            
    @discord.slash_command(description="Clear message in a channel as root")
    async def clear(self, ctx: discord.commands.context.ApplicationContext):
        Log.command(ctx.author.name + " is launching clear commands")
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
        Log.command(ctx.author.name + " is launching root commands with " + option)
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
        Log.command(ctx.author.name + " is launching send commands")
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
        Log.command(ctx.author.name + " is launching manage smartpoint commands with " + option)
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
    @discord.option("option", description="add/remove/show/update/rename", choices=["add", "remove", "show", "update", "rename"])
    @discord.option("wallpaper_name", require=True)
    @discord.option("url", require=False)
    @discord.option("price", int, require=False)
    @discord.option("level", int, require=False)
    @discord.option("new_name", str, require=False)
    async def manage_wallpaper(self, ctx: discord.commands.context.ApplicationContext, option: str, wallpaper_name: str, url: str = "", price: int = None, level: int = None, new_name: str = None):
        Log.command(ctx.author.name + " is launching manage wallpaper commands with " + option)
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
                    if not Utils.is_url_image(url):
                        await ctx.respond(self.__response_exception["url_not_an_image"])
                        return
                    wallpapers.add(wallpaper_name, url, self.__not_none(price), self.__not_none(level))
                    await ctx.respond(self.__response["wallpaper_added"])
                case "remove":
                    wallpapers.remove(Wallpaper(wallpaper_name))
                    await ctx.respond(self.__response["wallpaper_removed"])
                case "update":
                    wallpaper = Wallpaper(wallpaper_name)
                    
                    if url != "":
                        wallpaper.url = url
                    
                    if price != None:
                        wallpaper.price = price
                        
                    if level != None:
                        wallpaper.level = level
                    
                    await ctx.respond(self.__response["wallpaper_updated"])
                case "rename":
                    if new_name == None:
                        await ctx.respond(self.__response_exception["enter_new_name"])
                        return
                    
                    wallpaper = Wallpaper(wallpaper_name)
                    wallpaper.name = new_name
                    
                    await ctx.respond(self.__response["wallpaper_renamed"])
                case _:
                    await ctx.respond(self.__response_exception["option_not_found"])
        except requests.exceptions.MissingSchema:
            await ctx.respond(self.__response_exception["url_not_good_formated"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
    
    @discord.slash_command(description="Manage profile layout as root")
    @discord.option("option", description="add/remove/update/rename/show", choices=["add", "remove", "update", "rename", "show"])
    @discord.option("profile_layout_name", str, require=True)
    @discord.option("profile_picture_x", int, require=False)
    @discord.option("profile_picture_y", int, require=False)
    @discord.option("name_x", int, require=False)
    @discord.option("name_y", int, require=False)
    @discord.option("username_x", int, require=False)
    @discord.option("username_y", int, require=False)
    @discord.option("level_x", int, require=False)
    @discord.option("level_y", int, require=False)
    @discord.option("badge_x", int, require=False)
    @discord.option("badge_y", int, require=False)
    @discord.option("level_bar_x", int, require=False)
    @discord.option("level_bar_y", int, require=False)
    @discord.option("new_name", str, require=False)
    async def manage_profile_layout(self, ctx: discord.commands.context.ApplicationContext, option: str, profile_layout_name: str, profile_picture_x: int = None, profile_picture_y: int = None, name_x: int = None, name_y: int = None, username_x: int = None, username_y: int = None, level_x: int = None, level_y: int = None, badge_x: int = None, badge_y: int = None, level_bar_x: int = None, level_bar_y: int = None, new_name: str = None):
        Log.command(ctx.author.name + " is launching manage profile layout commands")
        try:
            if not await self.__check_if_root(ctx):
                return
            
            profile_layouts = ProfileLayouts()
            
            match option:
                case "show":
                    profile_layout = ProfileLayout(profile_layout_name)
                    await ctx.respond("**Name** " + profile_layout.name +
                                      "\n**Layout** " + str(profile_layout.layout.dict()))
                case "remove":
                    profile_layouts.remove(ProfileLayout(profile_layout_name))
                    await ctx.respond(self.__response["profile_layout_removed"])
                case "add":
                    layout = Layout(
                        Coords(self.__not_none(profile_picture_x), self.__not_none(profile_picture_y)),
                        Coords(self.__not_none(name_x), self.__not_none(name_y)),
                        Coords(self.__not_none(username_x), self.__not_none(username_y)),
                        Coords(self.__not_none(level_x), self.__not_none(level_y)),
                        Coords(self.__not_none(badge_x), self.__not_none(badge_y)),
                        Coords(self.__not_none(level_bar_x), self.__not_none(level_bar_y))
                    )
                    
                    profile_layouts.add(profile_layout_name, layout)
                    await ctx.respond(self.__response["profile_layout_added"])
                case "rename":
                    if new_name == None:
                        await ctx.respond(self.__response_exception["enter_new_name"])
                        return
                    profile_layout = ProfileLayout(profile_layout_name)
                    profile_layout.name = new_name
                    await ctx.respond(self.__response["profile_layout_renamed"])
                case "update":
                    profile_layout = ProfileLayout(profile_layout_name)
                    current_profile_layout = profile_layout.layout
                    layout = Layout(
                        Coords(self.__not_none(profile_picture_x, current_profile_layout.profile_picture.x), self.__not_none(profile_picture_y, current_profile_layout.profile_picture.y)),
                        Coords(self.__not_none(name_x, current_profile_layout.name.x), self.__not_none(name_y, current_profile_layout.name.y)),
                        Coords(self.__not_none(username_x, current_profile_layout.username.x), self.__not_none(username_y, current_profile_layout.username.y)),
                        Coords(self.__not_none(level_x, current_profile_layout.level.x), self.__not_none(level_y, current_profile_layout.level.y)),
                        Coords(self.__not_none(badge_x, current_profile_layout.badge.x), self.__not_none(badge_y, current_profile_layout.badge.y)),
                        Coords(self.__not_none(level_bar_x, current_profile_layout.level_bar.x), self.__not_none(level_bar_y, current_profile_layout.level_bar.y))
                    )
                    profile_layout.layout = layout
                    await ctx.respond(self.__response["profile_layout_updated"])
                case _:
                    await ctx.respond(self.__response_exception["option_not_found"])
            
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))
    
    @discord.slash_command(description="Manage role")
    @discord.option("option", description="add/remove/show", choices=["add", "remove", "show", "update"])
    @discord.option("role", discord.role.Role, require=True)
    @discord.option("level", int, require=False)
    async def manage_role(self, ctx: discord.commands.context.ApplicationContext, option: str, role: discord.role.Role, level: int = None):
        Log.command(ctx.author.name + " is launching manage role commands with " + option)
        try:
            if not await self.__check_if_root(ctx):
                return
            
            roles = Roles()

            role_id = str(role.id)
            
            if role.is_default():
                if option == "show":
                    await ctx.respond(self.__all_roles())
                else:
                    await ctx.respond(self.__response_exception["cannot_manage_default_role"])
                return 
            
            match option:
                case "show":
                    await ctx.respond("**Name** " + role.name + "\n**Level** " + str(Role(role_id).level))
                case "add":
                    roles.add(role_id, self.__not_none(level))
                    await ctx.respond(self.__response["role_added"])
                    await RoleUtils.update_all_user_role(ctx.guild)
                case "remove":
                    roles.remove(role_id)
                    await ctx.respond(self.__response["role_removed"])
                    await RoleUtils.update_all_user_role(ctx.guild)
                case "update":
                    Role(role_id).level = self.__not_none(level)
                    await ctx.respond(self.__response["role_updated"])
                    await RoleUtils.update_all_user_role(ctx.guild)
                case _:
                    await ctx.respond(self.__response_exception["option_not_found"])
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))


    async def __check_if_root(self, ctx: discord.commands.context.ApplicationContext) -> bool:
        if not User(str(ctx.author.id)).is_root:
            await ctx.respond(self.__response_exception["not_root"])
            return False
        return True
    
    def __not_none(self, s ,d = 0):
        if s is None:
            return d
        else:
            return s
    
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
    
    def __all_roles(self) -> str:
        roles = Roles().all
        if len(roles) == 0:
            return "No roles found"
        content = ""
        for role in roles:
            content += "**<@&" + role.discord_id + ">** " + str(role.level) + "\n"
        return content

    
def setup(bot: discord.bot.Bot):
    bot.add_cog(RootCommands(bot))