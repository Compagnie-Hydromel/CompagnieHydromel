import traceback
import discord
import requests
from libs.config import Config
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout
from libs.databases.models.guild import Guild
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.profile_layout import ProfileLayout
from libs.databases.models.role import Role
from libs.databases.models.user import User
from libs.databases.models.wallpaper import Wallpaper
from libs.exception.handler import Handler
from libs.log import Log
from libs.utils.utils import Utils
from libs.utils.role_utils import RoleUtils


class AdminCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()
        self.__error_handler = Handler()

    @discord.slash_command(description="Broadcast a message to a any channel as admin")
    @discord.option("channel", discord.abc.GuildChannel, require=True)
    @discord.option("message", require=True)
    async def broadcast(self, ctx: discord.commands.context.ApplicationContext, channel: discord.abc.GuildChannel, message: str):
        Log.command(ctx.author.name + " is launching broadcast commands")
        try:
            if not await self.__check_if_admin(ctx):
                return
            if not isinstance(channel, discord.abc.Messageable):
                await ctx.respond("Channel is not messageable.")
                return
            if channel.guild != ctx.guild:
                await ctx.respond(
                    "You cannot send a message in this channel, it is not in the same server."
                )
                return

            await channel.send(message.replace("\\n", "\n"))
            await ctx.respond("Message sent to " + channel.mention)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Send informations in information channel as admin")
    @discord.option("message", require=True)
    @discord.option("title", require=False)
    @discord.option("color", require=False)
    async def info(self, ctx: discord.commands.context.ApplicationContext, message: str, title: str = "Information", color: str = "#ffffff"):
        Log.command(ctx.author.name + " is launching info commands")
        try:
            if not await self.__check_if_admin(ctx):
                return
            guild = Guild.from_discord_id(ctx.guild.id)

            information_channel = self.__bot.get_channel(
                int(guild.information_channel_id))

            if information_channel == None:
                await ctx.respond("Information channel not found.")
                return
            if information_channel.guild != ctx.guild:
                await ctx.respond(
                    "You cannot send information in this channel, it is not the information channel of this server."
                )
                return

            if not isinstance(information_channel, discord.abc.Messageable):
                await ctx.respond("Information channel is not messageable.")
                return

            # WARNING: eval = evil
            # we check it before to avoid security issue
            embed = discord.Embed(title=title, description=message.replace(
                "\\n", "\n"), color=eval("0x" + Utils.check_color(color)))

            await information_channel.send(embed=embed)
            await ctx.respond("Message sent to information channel.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Set channel value as admin")
    @discord.option("key", require=True, choices=["information_channel", "monthlytop_channel"])
    @discord.option("value", require=True, type=discord.abc.GuildChannel)
    async def set_config(self, ctx: discord.commands.context.ApplicationContext, key: str, value: str):
        Log.command(ctx.author.name + " is launching set config commands")
        try:
            if not await self.__check_if_admin(ctx):
                return

            guild = Guild.from_discord_id(ctx.guild.id)

            match key:
                case "information_channel":
                    guild.information_channel_id = value.id
                case "monthlytop_channel":
                    guild.monthlytop_channel_id = value.id
                case _:
                    await ctx.respond("Invalid key, please use information_channel or monthlytop_channel.")
                    return

            guild.saveOrFail()

            await ctx.respond("Information channel set to " + value.mention)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Clear message in a channel as admin")
    async def clear(self, ctx: discord.commands.context.ApplicationContext):
        Log.command(ctx.author.name + " is launching clear commands")
        try:
            if not await self.__check_if_admin(ctx):
                return
            await ctx.respond("Clearing channel...")
            await ctx.channel.purge()
            await ctx.channel.send("Channel cleared by " + ctx.author.mention)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Send a message to a user as superadmin")
    @discord.option("user", discord.User, require=True)
    @discord.option("message", require=True)
    async def message_user(self, ctx: discord.commands.context.ApplicationContext, user: discord.User, message: str):
        Log.command(ctx.author.name + " is launching send commands")
        try:
            if not await self.__check_if_superadmin(ctx):
                return
            if not isinstance(user, discord.abc.Messageable):
                await ctx.respond("User is not messageable.")
                return

            await user.send(message.replace("\\n", "\n"))
            await ctx.respond("Message sent to " + user.mention)
        except discord.Forbidden:
            await ctx.respond("Cannot send message to this user, they may have blocked the bot or disabled DMs.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Manage smartpoint as admin")
    @discord.option("option", description="add/remove/show", choices=["add", "remove", "show"])
    @discord.option("user", discord.User, require=True)
    @discord.option("amount", int, require=False)
    async def manage_smartpoint(self, ctx: discord.commands.context.ApplicationContext, option: str, user: discord.User, amount: int = 0):
        Log.command(ctx.author.name +
                    " is launching manage smartpoint commands with " + option)
        try:
            if not await self.__check_if_admin(ctx):
                return

            user_in_db = GuildUser.from_user_discord_id_and_guild_discord_id(
                str(user.id), str(ctx.guild.id))

            match option:
                case "show":
                    await ctx.respond(user.display_name + " smartpoint: " + str(user_in_db.smartpoint))
                case "add" | "remove":
                    if amount < 1:
                        await ctx.respond("You must specify an amount greater than 0.")
                        return
                    if option == "add":
                        user_in_db.smartpoint += amount
                        await ctx.respond("" + str(amount) + " smartpoint added to " + user.display_name)
                    else:
                        user_in_db.smartpoint -= amount
                        await ctx.respond("" + str(amount) + " smartpoint removed from " + user.display_name)

                    user_in_db.saveOrFail()
                case _:
                    await ctx.respond("Option not found, please use add/remove/show.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Manage wallpaper as admin")
    @discord.option("option", description="add/remove/show/update/rename", choices=["add", "remove", "show", "update", "rename"])
    @discord.option("wallpaper_name", require=True)
    @discord.option("url", require=False)
    @discord.option("price", int, require=False)
    @discord.option("level", int, require=False)
    @discord.option("new_name", str, require=False)
    async def manage_wallpaper(self, ctx: discord.commands.context.ApplicationContext, option: str, wallpaper_name: str, url: str = "", price: int = None, level: int = None, new_name: str = None):
        Log.command(ctx.author.name +
                    " is launching manage wallpaper commands with " + option)
        try:
            if not await self.__check_if_admin(ctx):
                return

            match option:
                case "show":
                    wallpaper = Wallpaper.whereFirst(
                        name=wallpaper_name, guild_id=ctx.guild.id)
                    if wallpaper is None:
                        await ctx.respond("Wallpaper " + wallpaper_name + " not found")
                        return
                    await ctx.respond("**Name** " + wallpaper.name +
                                      "\n**url** " + wallpaper.url +
                                      "\n**price** " + str(wallpaper.price) + " smartpoint" +
                                      "\n**level to obtain** " + str(wallpaper.level))
                case "add":
                    Wallpaper.create(name=wallpaper_name, url=url,
                                     price=price or 0, level=level or 0, guild=Guild.from_discord_id(ctx.guild.id))
                    await ctx.respond("Wallpaper " + wallpaper_name + " added")
                case "remove":
                    wallpaper = Wallpaper.whereFirst(
                        name=wallpaper_name, guild_id=ctx.guild.id)
                    if wallpaper is None:
                        await ctx.respond("Wallpaper " + wallpaper_name + " not found")
                        return

                    wallpaper.delete()

                    await ctx.respond("Wallpaper " + wallpaper_name + " removed")
                case "update":
                    wallpaper = Wallpaper.whereFirst(
                        name=wallpaper_name, guild_id=ctx.guild.id)

                    if wallpaper is None:
                        await ctx.respond("Wallpaper " + wallpaper_name + " not found")
                        return

                    if url != "":
                        wallpaper.url = url

                    if price != None:
                        wallpaper.price = price

                    if level != None:
                        wallpaper.level = level

                    if new_name != None:
                        wallpaper.name = new_name

                    wallpaper.saveOrFail()

                    await ctx.respond("Wallpaper " + wallpaper_name + " updated")
                case _:
                    await ctx.respond("Option not found, please use add/remove/show/update/rename.")
        except requests.exceptions.MissingSchema:
            await ctx.respond("Invalid URL provided. Please ensure it starts with http:// or https://.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Manage profile layout as superadmin")
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
        Log.command(ctx.author.name +
                    " is launching manage profile layout commands")
        try:
            if not await self.__check_if_superadmin(ctx):
                return

            match option:
                case "show":
                    profile_layout = ProfileLayout.whereFirst(
                        name=profile_layout_name)
                    if profile_layout is None:
                        await ctx.respond("Profile layout " + profile_layout_name + " not found")
                        return
                    await ctx.respond("**Name** " + profile_layout.name +
                                      "\n**Layout** " + str(profile_layout.layout.dict()))
                case "remove":
                    profilelayout = ProfileLayout.whereFirst(
                        name=profile_layout_name)
                    if profilelayout is None:
                        await ctx.respond("Profile layout " + profile_layout_name + " not found")
                        return
                    profilelayout.delete()
                    await ctx.respond("Profile layout " + profile_layout_name + " removed")
                case "add":
                    layout = Layout(
                        Coords(profile_picture_x or 0,
                               profile_picture_y or 0),
                        Coords(name_x or 0,
                               name_y or 0),
                        Coords(username_x or 0,
                               username_y or 0),
                        Coords(level_x or 0,
                               level_y or 0),
                        Coords(badge_x or 0,
                               badge_y or 0),
                        Coords(level_bar_x or 0,
                               level_bar_y or 0)
                    )

                    ProfileLayout.createFromLayout(profile_layout_name, layout)
                    await ctx.respond("Profile layout " + profile_layout_name + " added")
                case "update":
                    profile_layout = ProfileLayout.from_name(
                        profile_layout_name)

                    if profile_layout is None:
                        await ctx.respond("Profile layout " + profile_layout_name + " not found")
                        return

                    current_profile_layout = profile_layout.layout
                    layout = Layout(
                        Coords(profile_picture_x or current_profile_layout.profile_picture.x,
                               profile_picture_y or current_profile_layout.profile_picture.y),
                        Coords(name_x or current_profile_layout.name.x,
                               name_y or current_profile_layout.name.y),
                        Coords(username_x or current_profile_layout.username.x,
                               username_y or current_profile_layout.username.y),
                        Coords(level_x or current_profile_layout.level.x,
                               level_y or current_profile_layout.level.y),
                        Coords(badge_x or current_profile_layout.badge.x,
                               badge_y or current_profile_layout.badge.y),
                        Coords(level_bar_x or current_profile_layout.level_bar.x,
                               level_bar_y or current_profile_layout.level_bar.y)
                    )
                    if new_name is not None:
                        profile_layout.name = new_name
                    profile_layout.layout = layout
                    profile_layout.saveOrFail()
                    await ctx.respond("Profile layout " + profile_layout_name + " updated")
                case _:
                    await ctx.respond("Option not found, please use add/remove/show/update/rename.")

        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Manage role")
    @discord.option("option", description="add/remove/show", choices=["list", "add", "remove", "show", "update"])
    @discord.option("role", discord.role.Role, require=False)
    @discord.option("level", int, require=False)
    async def manage_role(self, ctx: discord.commands.context.ApplicationContext, option: str, role: discord.role.Role, level: int = None):
        Log.command(ctx.author.name +
                    " is launching manage role commands with " + option)
        try:
            if not await self.__check_if_admin(ctx):
                return

            guild = Guild.from_discord_id(ctx.guild.id)

            if not role and option != "list":
                await ctx.respond("You must specify a role.")
                return

            match option:
                case "list":
                    await ctx.respond(self.__all_roles(ctx.guild))
                case "show":
                    await ctx.respond("**Name** " + role.name + "\n**Level** " + str(Role.from_discord_id(role.id).level))
                case "add":
                    Role.createOrFail(discord_id=role.id,
                                      level=level or 1, guild=guild)
                    await ctx.respond("Role added with level " + str(level or 1))
                    await RoleUtils.update_all_user_role(ctx.guild)
                case "remove":
                    role = Role.from_discord_id(role.id)
                    if role is None:
                        await ctx.respond(f"Role not found")
                        return
                    role.delete()
                    await ctx.respond(f"Role removed")
                    await RoleUtils.update_all_user_role(ctx.guild)
                case "update":
                    role: Role = Role.from_discord_id(role.id)
                    if role is None:
                        await ctx.respond(f"Role not found")
                        return
                    role.level = level or 1
                    role.saveOrFail()
                    await ctx.respond(f"Role updated with level " + str(role.level))
                    await RoleUtils.update_all_user_role(ctx.guild)
                case _:
                    await ctx.respond("Option not found, please use add/remove/show/update.")
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    @discord.slash_command(description="Move all users in a voice channel to a another voice channel")
    @discord.option("from_channel", discord.VoiceChannel, require=True)
    @discord.option("to_channel", discord.VoiceChannel, require=True)
    async def move_all_users(self, ctx: discord.commands.context.ApplicationContext, from_channel: discord.VoiceChannel, to_channel: discord.VoiceChannel):
        Log.command(ctx.author.name + " is launching move all users commands")
        try:
            await ctx.defer()
            if not await self.__check_if_admin(ctx):
                return

            if from_channel == to_channel:
                await ctx.respond("You cannot move users to the same channel.")
                return

            if len(from_channel.members) == 0:
                await ctx.respond("No users in " + from_channel.name + ", nothing to move.")
                return

            for member in from_channel.members:
                await member.move_to(to_channel)

            Log.info("Moving all users from " +
                     from_channel.name + " to " + to_channel.name)

            await ctx.respond("Moved all users from " + from_channel.name + " to " + to_channel.name)
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(e, traceback.format_exc()))

    async def __check_if_superadmin(self, ctx: discord.commands.context.ApplicationContext) -> bool:
        if not User.from_discord_id(str(ctx.author.id)).is_superadmin:
            await ctx.respond("You don't have permission to use this command.")
            return False
        return True

    async def __check_if_admin(self, ctx: discord.commands.context.ApplicationContext) -> bool:
        if not ctx.guild:
            await ctx.respond("Command can only be used in a server.")
            return False

        guilduser = GuildUser.from_user_discord_id_and_guild_discord_id(
            str(ctx.author.id), str(ctx.guild.id))

        if not guilduser.is_admin:
            await ctx.respond("You don't have permission to use this command.")
            return False
        return True

    def __all_roles(self, guild) -> str:
        roles = Guild.from_discord_id(guild.id).roles.orderBy("level")
        if len(roles) == 0:
            return "No roles found"
        content = ""
        for role in roles:
            content += "**<@&" + role.discord_id + \
                ">** " + str(role.level) + "\n"
        return content


def setup(bot: discord.bot.Bot):
    bot.add_cog(AdminCommands(bot))
