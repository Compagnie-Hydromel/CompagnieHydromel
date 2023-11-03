import random
import traceback
import discord
from discord.ext import tasks

from libs.databases.user.user import User
from libs.log import Log, LogType

class Listener(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.loop_check_point_in_vocal.start()

    def cog_unload(self):
        self.loop_check_point_in_vocal.cancel()

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        Log.logMessage(message.channel, message.content, message.author.name, self.__bot.user.name, onlyDm=True)
        
        if message.author == self.__bot.user:
            return

        User(str(message.author.id)).add_point()
        
    @discord.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        log_content = "deleted a message : " + message.content
        Log.logMessage(message.channel, log_content, message.author.name, self.__bot.user.name, onlyDm=True)
        
    @discord.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        log_content = "edited a message : " + before.content + " -> " + after.content
        Log.logMessage(before.channel, log_content, before.author.name, self.__bot.user.name, onlyDm=True)

    @tasks.loop(seconds = 299)
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
                                if len(members) == 1 and random.randint(0,3) != 2:
                                    return
                                user = User(str(member.id))
                                user.add_point()
        except:
            Log(traceback.format_exc(), LogType.ERROR)

def setup(bot: discord.bot.Bot):
    bot.add_cog(Listener(bot))