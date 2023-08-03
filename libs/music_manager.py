import discord
import wavelink

from libs.exception.music.not_connected_to_voice_channel_exception import NotConnectedToVoiceChannelException
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException

class MusicManager:
    """Class that manage the music.
    """
    def __init__(self) -> None:
        """Constructor of MusicManager class.
        """
        self.voice_clients: discord.voice_client.VoiceClient = None
        self.voice_queues: wavelink.Queue = wavelink.Queue()
    
    async def play(self, voice_state: discord.VoiceState | None, song: wavelink.abc.Playable):        
        """Play a song.

        Args:
            voice_state (discord.VoiceState | None): Voice state of the user if it's connected to a voice channel if is not it's none.
            song (wavelink.abc.Playable): The song to play.
        
        Raises:
            NotConnectedToVoiceChannelException: if the user is not connected to a voice channel.
        """
        await self.__connect_if_not_connected(voice_state)
        
        self.voice_queues.put_at_front(song)
        if not self.voice_clients.is_playing():
            await self.skip()
    
    async def skip(self):
        """Skip the current song.

        Raises:
            NothingLeftInQueueException: if the queue is empty.
        """        
        if self.voice_queues.is_empty:
            raise NothingLeftInQueueException
        await self.voice_clients.play(self.voice_queues.pop())
    
    async def resume(self):
        """Resume the current song.
        """
        if self.voice_clients.is_paused():
            await self.voice_clients.resume()
    
    async def search(self, search: str) -> wavelink.abc.Playable:
        """Search a song.

        Args:
            search (str): the string to search on youtube.

        Returns:
            wavelink.abc.Playable: the song to play.
        """
        return await wavelink.YouTubeTrack.search(query=search, return_first=True)
        
    async def stop(self, disconnect: bool = True):
        """Stop the current song.

        Args:
            disconnect (bool, optional): if you need to disconnect the bot after stopping music. Defaults to True.
        """
        await self.voice_clients.stop()
        if disconnect:
            await self.disconnect()
    
    async def disconnect(self):
        """Disconnect the bot from the voice channel.
        """
        await self.voice_clients.disconnect()
        self.voice_queues.clear()
        self.voice_clients = None
    
    async def pause(self):
        """Pause the current song."""
        if not self.voice_clients.is_paused():
            await self.voice_clients.pause()
        
    async def __connect_if_not_connected(self, voice_state: discord.VoiceState):
        """Connect to the voice channel if the bot is not connected.

        Args:
            voice_state (discord.VoiceState): Voice state of the user if it's connected to a voice channel if is not it's none.

        Raises:
            NotConnectedToVoiceChannelException: if the user is not connected to a voice channel.
        """
        if not self.voice_clients:
            if voice_state == None:
                raise NotConnectedToVoiceChannelException
            self.voice_clients = await voice_state.channel.connect(cls=wavelink.Player)