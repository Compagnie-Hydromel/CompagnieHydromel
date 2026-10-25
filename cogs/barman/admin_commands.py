import traceback
import os
import uuid
import discord
import requests
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout
from libs.databases.models.guild import Guild
from libs.databases.models.scheduled_message import ScheduledMessage
from libs.databases.models.guild_user import GuildUser
from libs.databases.models.profile_layout import ProfileLayout
from libs.databases.models.user import User
from libs.databases.models.wallpaper import Wallpaper
from libs.exception.handler import Handler
from libs.log import Log
from libs.utils.utils import Utils


class AdminCommands(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
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

    @discord.slash_command(description="Configure recurring messages as admin")
    @discord.option("option", choices=["set", "show", "remove", "list"], require=True)
    @discord.option("name", str, require=False)
    @discord.option("channel", discord.abc.GuildChannel, require=False)
    @discord.option("message", str, require=False)
    @discord.option("day", choices=["daily", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], require=False)
    @discord.option("time", str, require=False, description="Time in HH:MM format")
    @discord.option("timezone", str, require=False, description="IANA timezone, e.g. Europe/Zurich")
    @discord.option("attachment", discord.Attachment, require=False)
    @discord.option("remove_attachment", bool, require=False)
    async def automatic_message(self, ctx: discord.commands.context.ApplicationContext,
                                option: str, name: str = None,
                                channel: discord.abc.GuildChannel = None,
                                message: str = "", day: str = None,
                                time: str = None,
                                timezone: str = "Europe/Zurich",
                                attachment: discord.Attachment = None,
                                remove_attachment: bool = False):
        Log.command(ctx.author.name + " is configuring an automatic message")
        try:
            if not await self.__check_if_admin(ctx):
                return

            guild = Guild.from_discord_id(ctx.guild.id)
            if option != "list" and not name:
                await ctx.respond("You must specify a configuration name.")
                return
            configuration = ScheduledMessage.by_name_and_guild(name, guild)

            match option:
                case "set":
                    if channel is None or message is None or day is None or time is None:
                        await ctx.respond(
                            "You must specify a channel, message, day, and time.")
                        return
                    if channel.guild != ctx.guild:
                        await ctx.respond("The channel must belong to this server.")
                        return
                    if not isinstance(channel, discord.abc.Messageable):
                        await ctx.respond("Channel is not messageable.")
                        return

                    try:
                        ScheduledMessage.validate_schedule(time, timezone)
                    except ValueError as error:
                        await ctx.respond(str(error))
                        return

                    content = message.replace("\\n", "\n")
                    attachment_path = None
                    if attachment is not None:
                        extension = re.sub(
                            r"[^a-zA-Z0-9.]", "",
                            os.path.splitext(attachment.filename)[1])[:16]
                        attachment_path = (
                            "local://scheduled_messages/" + uuid.uuid4().hex +
                            extension)
                        self.storage.put(
                            await attachment.read(), attachment_path)
                    if configuration is None:
                        ScheduledMessage.createOrFail(
                            name=name, channel_id=str(channel.id),
                            message=content, day=day, time=time,
                            timezone=timezone,
                            attachment_path=attachment_path,
                            attachment_name=(attachment.filename
                                             if attachment else None),
                            guild=guild)
                    else:
                        old_attachment_path = configuration.attachment_path
                        configuration.channel_id = str(channel.id)
                        configuration.message = content
                        configuration.day = day
                        configuration.time = time
                        configuration.timezone = timezone
                        if attachment is not None:
                            configuration.attachment_path = attachment_path
                            configuration.attachment_name = attachment.filename
                        elif remove_attachment:
                            configuration.attachment_path = None
                            configuration.attachment_name = None
                        configuration.saveOrFail()
                        if ((attachment is not None or remove_attachment) and
                                old_attachment_path):
                            self.storage.delete(old_attachment_path)
                    await ctx.respond(
                        f"Automatic message **{name}** will be sent "
                        f"{day} at {time} ({timezone}) in {channel.mention}.")
                case "show":
                    if configuration is None:
                        await ctx.respond(f"Automatic message **{name}** was not found.")
                        return
                    await ctx.respond(
                        f"**{configuration.name}**\n"
                        f"Channel: <#{configuration.channel_id}>\n"
                        f"Schedule: {configuration.day} at {configuration.time} "
                        f"({configuration.timezone})\n"
                        f"Attachment: {configuration.attachment_name or 'None'}\n"
                        f"Message:\n{configuration.message}")
                case "remove":
                    if configuration is None:
                        await ctx.respond(f"Automatic message **{name}** was not found.")
                        return
                    if configuration.attachment_path:
                        self.storage.delete(configuration.attachment_path)
                    configuration.delete()
                    await ctx.respond(f"Automatic message **{name}** removed.")
                case "list":
                    configurations = guild.scheduledmessages
                    if len(configurations) == 0:
                        await ctx.respond("No automatic messages are configured.")
                        return
                    lines = [
                        f"**{item.name}** — {item.day} at {item.time} "
                        f"({item.timezone}) in <#{item.channel_id}>"
                        for item in configurations
                    ]
                    await ctx.respond("\n".join(lines))
        except Exception as e:
            await ctx.respond(self.__error_handler.response_handler(
                e, traceback.format_exc()))

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


def setup(bot: discord.bot.Bot):
    bot.add_cog(AdminCommands(bot))
