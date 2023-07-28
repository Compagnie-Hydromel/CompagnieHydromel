import  discord

from libs.databases.user import User
from libs.log import Log, LogType

class Listener(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self._bot = bot

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        Log.logMessage(message.channel, message.content, message.author.name, self._bot.user.name)
        
        if message.author == self._bot.user:
            return
        
    @discord.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        log_content = "deleted a message : " + message.content
        Log.logMessage(message.channel, log_content, message.author.name, self._bot.user.name)
        
    @discord.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        log_content = "edited a message : " + before.content + " -> " + after.content
        Log.logMessage(before.channel, log_content, before.author.name, self._bot.user.name)
    
    @discord.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        Log(member.name + " joined the server " + member.guild.name, LogType.INFO)
        User(str(member.id)).add_point()
        
    @discord.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        Log(member.name + " left the server " + member.guild.name, LogType.INFO)

def setup(bot: discord.bot.Bot):
    bot.add_cog(Listener(bot))