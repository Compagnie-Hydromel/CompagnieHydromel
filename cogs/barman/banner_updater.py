import traceback
import  discord
from libs.banner_bar_creator import BannerBarCreator
from libs.config import Config
from libs.log import Log, LogType

class BannerUpdater(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.__config = Config()
        
    def __get_bar_image(self) -> str:
        guild_id = self.__config.value["banner"]["guild_id"]
        coords = self.__config.value["banner"]["coords"]
        people = {}
        guild = self.__bot.get_guild(guild_id)
        
        """
        To generate people info like this:
        
        people = {
            'bar': [
                {"username": "People 1", "profil": "https://discord.com/path/to/profile/picture" },
                ...
            ], 'table1': [
                ...
            ], ...
        }
        """
        for coord in coords:
            people[coord] = []
            vocal_id = coords[coord]["id"]
            if vocal_id == 0:
                Log("BannerUpdater: The vocal id of " + coord + " is 0, so it will be ignored.", LogType.WARNING)
                continue
            vocal = self.__get_voice_channel(vocal_id, guild)
            for member in vocal.members:
                avatar_url = member.display_avatar.url
                people[coord].append({"username": member.name, "profil": avatar_url })

        return BannerBarCreator('.banner.png', self.__config.value["banner"]["banner_image"], coords, people).file_path

    def __get_voice_channel(self, id: int, guild: discord.guild) -> discord.VoiceChannel or None:
        channels = guild.channels
        for i in channels:
            if isinstance(i, discord.VoiceChannel) and i.id == id:
                return i
        return None
    
    @discord.Cog.listener()
    async def on_voice_state_update(self, members: discord.member, before: discord.VoiceChannel, after: discord.VoiceChannel) -> None:
        try:
            if self.__config.value["banner"]["enable"]:
                image_url = self.__get_bar_image()
                with open(image_url, "rb") as image:
                    Log("Banner updated in " + image_url, LogType.INFO)
                    await self.__bot.get_guild(self.__config.value["banner"]["guild_id"]).edit(banner=image.read())
        except:
            Log(traceback.format_exc(), LogType.ERROR)

def setup(bot: discord.bot.Bot):
    bot.add_cog(BannerUpdater(bot))
