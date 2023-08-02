import discord
from time import sleep
from libs.config import Config
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException
from libs.log import Log
import wavelink
import os

class Music(discord.Cog):
    voice_clients: dict[int: discord.voice_client.VoiceClient] = {}
    voice_queues: dict[int: list[wavelink.Queue]] = {}
    
    def __init__(self, bot) -> None:
        self.__bot = bot
        self.__music_config = Config().value["music"]
    
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
        try:
            await self.__skip(player.guild.id)
        except(NothingLeftInQueueException):
            await self.__disconnect(player.guild.id)

    @discord.slash_command(description="Command that can play music that we want.")
    @discord.option("search", description="Search or youtube link")
    async def play(self, ctx : discord.ApplicationContext, *, search: str):
        song = await self.__search(ctx.guild.id, search)
        await self.__play(ctx.guild.id, ctx.author.voice.channel, song)

    @discord.slash_command(description="Command that stop the music and make the bot leave the channel.")
    async def stop(self, ctx : discord.ApplicationContext):
        await self.__stop(ctx.guild.id)
    
    @discord.slash_command(description="Command that pause the music.")
    async def pause(self, ctx : discord.ApplicationContext):
        await self.__pause(ctx.guild.id)
        
    @discord.slash_command(description="Command that resume the music.")
    async def resume(self, ctx : discord.ApplicationContext):
        await self.__resume(ctx.guild.id)
    
    @discord.slash_command(description="Command that skip the music.")
    async def skip(self, ctx : discord.ApplicationContext):
        await self.__skip(ctx.guild.id)
    
    @discord.slash_command(description="Command that get the queue. (max 6 music show)")
    async def queue(self, ctx : discord.ApplicationContext):
        pass
        
    @discord.slash_command(description="Command to get the current music.")
    async def now(self, ctx : discord.ApplicationContext):
        pass
    
    async def __play(self, guild_id: int, voice_channel: discord.VoiceChannel, song: wavelink.abc.Playable):
        self.__add_voice_client_if_not_exist(guild_id)
        
        await self.__connect_if_not_connected(guild_id, voice_channel)
        
        self.voice_queues[guild_id].put(song)
        if not self.voice_clients[guild_id].is_playing():
            await self.__play_next_in_queue(guild_id)
    
    async def __skip(self, guild_id: int):
        await self.__play_next_in_queue(guild_id)
    
    async def __resume(self, guild_id: int):
        if self.voice_clients[guild_id].is_paused():
            await self.voice_clients[guild_id].resume()
    
    async def __search(self, guild_id: int, search: str) -> wavelink.abc.Playable:
        return await wavelink.YouTubeTrack.search(query=search, return_first=True)
    
    async def __play_next_in_queue(self, guild_id: int):
        if self.voice_queues[guild_id].is_empty:
            raise NothingLeftInQueueException
        await self.voice_clients[guild_id].play(self.voice_queues[guild_id].pop())
        
    async def __connect_if_not_connected(self, guild_id: int, voice_channel: discord.VoiceChannel):
        if not self.voice_clients[guild_id]:
            self.voice_clients[guild_id] = await voice_channel.connect(cls=wavelink.Player)
        
    async def __stop(self, guild_id: int):
        await self.voice_clients[guild_id].stop()
        await self.__disconnect(guild_id)
    
    async def __disconnect(self, guild_id: int):
        await self.voice_clients[guild_id].disconnect()
        self.voice_queues[guild_id].clear()
        self.voice_clients[guild_id] = None
    
    async def __pause(self, guild_id: int):
        if not self.voice_clients[guild_id].is_paused():
            await self.voice_clients[guild_id].pause()
        
    def __add_voice_client_if_not_exist(self, guild_id: int):
        if guild_id not in self.voice_clients:
            self.voice_clients[guild_id] = None
        if guild_id not in self.voice_queues:
            self.voice_queues[guild_id] = wavelink.Queue()       

def setup(bot):
    if Config().value["music"]["enable"]:
        if os.getenv("LAVALINK_PASSWORD") == None:
            Log("No lavalink password found.")
        else: 
            bot.add_cog(Music(bot))