import  discord

from libs.databases.user import User
from libs.log import Log, LogType

class Listener(discord.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self._bot = bot

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        Log.logMessage(message.channel, message.content, message.author.name, self._bot.user.name, onlyDm=True)
        
        if message.author == self._bot.user:
            return

def setup(bot: discord.bot.Bot):
    bot.add_cog(Listener(bot))