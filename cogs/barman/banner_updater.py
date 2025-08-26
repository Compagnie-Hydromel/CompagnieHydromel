import traceback
import discord
from libs.databases.models.guild import Guild
from libs.image_factory.banner_bar_creator import BannerBarCreator
from libs.log import Log
from typing import Union


class BannerUpdater(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot

    def __get_bar_image(self, db_guild: Guild) -> str:
        coords = []
        for voice_channel in db_guild.voicechannels:
            coords.append({
                "id": int(voice_channel.discord_id),
                "x": voice_channel.x,
                "y": voice_channel.y
            })
        people = {}
        guild = self.__bot.get_guild(int(db_guild.discord_id))

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

        return BannerBarCreator('.banner.png', db_guild.banner_image, coords, people).file_path

    def __get_voice_channel(self, id: int, guild: discord.guild) -> Union[discord.VoiceChannel, None]:
        channels = guild.channels
        for i in channels:
            if isinstance(i, discord.VoiceChannel) and i.id == id:
                return i
        return None

    @discord.Cog.listener()
    async def on_voice_state_update(self, _members: discord.member, _before: discord.VoiceChannel, _after: discord.VoiceChannel) -> None:
        try:
            guild_id = members.guild.id
            guild = Guild.from_discord_id(guild_id)
            if guild.banner_image:
                image_url = self.__get_bar_image(guild)
                Log.info("Updating banner " + str(image_url))
                with open(image_url, "rb") as image:
                    await self.__bot.get_guild(guild_id).edit(banner=image.read())
                    Log.info("Banner updated " + str(image_url))
        except:
            Log.error(traceback.format_exc())


def setup(bot: discord.bot.Bot):
    bot.add_cog(BannerUpdater(bot))
