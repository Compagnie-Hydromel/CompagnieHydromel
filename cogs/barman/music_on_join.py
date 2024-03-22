import  discord
from libs.config import Config
from libs.exception.music.already_playing_exception import AlreadyPlayingException

from libs.log import Log
from libs.music.guild_music_manager import GuildMusicManager
import wavelink
import os

from libs.music.music_manager import MusicManager

class MusicOnJoin(discord.Cog):
    def __init__(self, bot: discord.bot.Bot) -> None:
        self.__bot = bot
        self.config = Config()
        self.__music_config = self.config.value["music"]
        self.__music_on_join_config = self.__music_config["music_on_join"]
        self.__guild_music_manager = GuildMusicManager()
    
    @discord.Cog.listener()
    async def on_ready(self):
        await self.lavalink_nodes_connect()
        
    async def lavalink_nodes_connect(self):
        """Connect to our Lavalink nodes."""
        
        await wavelink.NodePool.create_node(
            bot=self.__bot,
            host=self.__music_config["lavalink_ip"],
            port=self.__music_config["lavalink_port"],
            password=os.getenv("LAVALINK_PASSWORD")
        )
        
    @discord.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        match reason:
            case "FINISHED": 
                await self.__guild_music_manager.get(player.guild.id).disconnect()
                Log.info("Disconnect bot in " + player.channel.name)

        
    @discord.Cog.listener()
    async def on_voice_state_update(self, members: discord.member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        if members.id == self.__bot.user.id:
            return
        if before.channel and after.channel or not before.channel:
            music_manager = self.__guild_music_manager.get(after.channel.guild.id)
            
            search_query = self.__get_music_query(str(members.id))
            
            if search_query == "":
                return
            
            song = await music_manager.search(search_query)
            while True:
                try:
                    await music_manager.play(members.voice, song)
                    await members.guild.me.edit(mute=False, deafen=False)
                except AlreadyPlayingException:
                    await music_manager.disconnect()
                    continue
                break
            
    def __get_music_query(self,member_id: str):
        if member_id in self.__music_on_join_config["discord_id_to_song"]:
            return self.__music_on_join_config["discord_id_to_song"][member_id]
        return self.__music_on_join_config["default_song"]
        
def setup(bot: discord.bot.Bot):
    if Config().value["music"]["music_on_join"]["enable"]:
        if os.getenv("LAVALINK_PASSWORD") == None:
            Log.warning("No lavalink password found.")
        else: 
            bot.add_cog(MusicOnJoin(bot))
