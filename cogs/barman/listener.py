import  discord

from libs.databases.user import User
from libs.log import Log, LogType

class Listener(discord.Cog):
    def __init__(self, bot) -> None:
        self._bot = bot

    @discord.Cog.listener()
    async def on_message(self, message):
        channel = ""
        if not isinstance(message.channel, discord.DMChannel):
            channel = message.channel.name
        Log("(" + channel + ")" + message.author.name + ": " + message.content, LogType.MESSAGE)
        
        if message.author == self._bot.user:
            return

def setup(bot):
    bot.add_cog(Listener(bot))