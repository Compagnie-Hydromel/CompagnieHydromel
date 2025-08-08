import traceback
import discord
from libs.image_factory.banner_bar_creator import BannerBarCreator
from libs.config import Config
from libs.log import Log
from typing import Union


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
            1131446231160328212: [
                {"username": "People 1", "profil": "https://discord.com/path/to/profile/picture" }
            ],
            1131446231160328212: [
                ...
            ],
            ...
        }
        """
        for coord in coords:
            people[coord["id"]] = []
            vocal_id = coord["id"]
            if vocal_id == 0:
                Log.warning("BannerUpdater: The vocal id of " +
                            coord + " is 0, so it will be ignored.")
                continue
            vocal = self.__get_voice_channel(vocal_id, guild)
            for member in vocal.members:
                avatar_url = member.display_avatar.url
                people[coord["id"]].append(
                    {"username": member.name, "profil": avatar_url})

        return BannerBarCreator('.banner.png', self.__config.value["banner"]["banner_image"], coords, people).file_path

    def __get_voice_channel(self, id: int, guild: discord.guild) -> Union[discord.VoiceChannel, None]:
        channels = guild.channels
        for i in channels:
            if isinstance(i, discord.VoiceChannel) and i.id == id:
                return i
        return None

    @discord.Cog.listener()
    async def on_voice_state_update(self, _members: discord.member, _before: discord.VoiceChannel, _after: discord.VoiceChannel) -> None:
        try:
            if self.__config.value["banner"]["enable"]:
                image_url = self.__get_bar_image()
                Log.info("Updating banner " + str(image_url))
                with open(image_url, "rb", encoding="utf-8") as image:
                    await self.__bot.get_guild(self.__config.value["banner"]["guild_id"]).edit(banner=image.read())
                    Log.info("Banner updated " + str(image_url))
        except:
            Log.error(traceback.format_exc())


def setup(bot: discord.bot.Bot):
    bot.add_cog(BannerUpdater(bot))
