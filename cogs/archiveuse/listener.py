import random
import traceback
import discord
from discord.ext import tasks

from libs.config import Config
from libs.databases.model.user.user import User
from libs.log import Log
from libs.utils.level_utils import LevelUtils


class Listener(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.loop_check_point_in_vocal.start()

    def cog_unload(self):
        self.loop_check_point_in_vocal.cancel()

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        Log.message(message.channel, message.content,
                    message.author.name, self.__bot.user.name, onlyDm=True)

        if message.author == self.__bot.user:
            return

        await LevelUtils.add_point(message.author)

    @discord.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        log_content = "deleted a message : " + message.content
        Log.message(message.channel, log_content,
                    message.author.name, self.__bot.user.name, onlyDm=True)

    @discord.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        log_content = "edited a message : " + before.content + " -> " + after.content
        Log.message(before.channel, log_content, before.author.name,
                    self.__bot.user.name, onlyDm=True)

    @tasks.loop(seconds=299)
    async def loop_check_point_in_vocal(self):
        try:
            guilds = self.__bot.guilds
            for guild in guilds:
                channels = guild.channels
                for channel in channels:
                    if isinstance(channel, discord.VoiceChannel):
                        members = channel.members
                        for member in members:
                            if not member.voice.self_deaf:
                                if len(members) == 1 and random.randint(0, 3) != 2:
                                    return

                                await LevelUtils.add_point(member)

        except:
            Log.error(traceback.format_exc())


def setup(bot: discord.bot.Bot):
    bot.add_cog(Listener(bot))
