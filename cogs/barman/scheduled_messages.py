import datetime
import traceback
from io import BytesIO
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from libs.databases.models.scheduled_message import ScheduledMessage
from libs.exception.handler import Handler
from libs.log import Log
from libs.storages.storage import Storage


class ScheduledMessages(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__error_handler = Handler()
        self.__storage = Storage()
        self.send_due_messages.start()

    def cog_unload(self):
        self.send_due_messages.cancel()

    @tasks.loop(seconds=30)
    async def send_due_messages(self):
        for configuration in ScheduledMessage.all():
            try:
                await self.__send_if_due(configuration)
            except Exception as error:
                self.__error_handler.response_handler(
                    error, traceback.format_exc())

    @send_due_messages.before_loop
    async def before_send_due_messages(self):
        await self.__bot.wait_until_ready()

    async def __send_if_due(self, configuration: ScheduledMessage) -> None:
        now = datetime.datetime.now(ZoneInfo(configuration.timezone))
        today = now.date().isoformat()
        scheduled_day = configuration.day.lower()
        weekdays = ("monday", "tuesday", "wednesday",
                    "thursday", "friday", "saturday", "sunday")
        if scheduled_day != "daily" and scheduled_day != weekdays[now.weekday()]:
            return
        if now.strftime("%H:%M") != configuration.time:
            return
        if configuration.last_sent_date == today:
            return

        channel = self.__bot.get_channel(int(configuration.channel_id))
        if (channel is None or not isinstance(channel, discord.abc.Messageable) or
                str(channel.guild.id) != str(configuration.guild.discord_id)):
            Log.warning(
                f"Scheduled message channel {configuration.channel_id} was not found")
            return

        attachment = None
        if configuration.attachment_path:
            content = self.__storage.get(configuration.attachment_path)
            if content is None:
                Log.warning(
                    f"Scheduled message attachment {configuration.attachment_path} "
                    "was not found")
            else:
                attachment = discord.File(
                    BytesIO(content), filename=configuration.attachment_name)

        if configuration.message:
            await channel.send(configuration.message, file=attachment)
        else:
            await channel.send(file=attachment)
        configuration.last_sent_date = today
        configuration.saveOrFail()


def setup(bot: discord.bot.Bot):
    bot.add_cog(ScheduledMessages(bot))
