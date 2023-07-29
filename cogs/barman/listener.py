import  discord
from libs.banner_bar_creator import BannerBarCreator

from libs.databases.user import User
from libs.log import Log, LogType

class Listener(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self._bot = bot
        
    def get_bar_image(self, vocal: discord.VoiceChannel):
        coords = {
            'bar': {"w":390,"h":215, "id": 928302763551645696},
            'table1': {"w":110,"h":279, "id": 928302830463377418},
            'table2': {"w":607,"h":293, "id": 928303177831432255},
            'table3': {"w":450,"h":457, "id": 928351848811888690}
        }
        people = {}

        for coord in coords:
            people[coord] = []
            for member in vocal.members:
                avatar = member.avatar.url
                if member.guild_avatar != None:
                    avatar = member.guild_avatar.url
                people[coord].append({"username": member.name, "profil": avatar })

        return BannerBarCreator('.taverne.png' ,'img/taverne.jpg', coords, people)

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
        
    @discord.Cog.listener()
    async def on_voice_state_update(self, members, before, after):
        with open(self.get_bar_image(), "rb") as image:
            await self._bot.get_guild(928279859627696179).edit(banner=image.read())

def setup(bot: discord.bot.Bot):
    bot.add_cog(Listener(bot))