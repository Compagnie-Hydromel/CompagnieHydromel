import discord
import wavelink
from libs.exception.music.already_playing_exception import AlreadyPlayingException
from libs.exception.music.no_music_playing import NoMusicPlaying
from libs.exception.music.no_playing_instance_exception import NoPlayingInstanceException
from libs.exception.music.no_result_found_exception import NoResultsFoundException

from libs.exception.music.not_connected_to_voice_channel_exception import NotConnectedToVoiceChannelException
from libs.exception.music.nothing_left_in_back_queue import NothingLeftInBackQueueException
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException

class MusicManager:
    """Class that manage the music.
    """
    def __init__(self) -> None:
        """Constructor of MusicManager class.
        """
        self.voice_clients: discord.VoiceClient = None
        self.voice_queues: wavelink.Queue = wavelink.Queue()
        self.voice_back: wavelink.Queue = wavelink.Queue()
    
    async def play(self, voice_state: discord.VoiceState | None, song: wavelink.abc.Playable):        
        """Play a song.

        Args:
            voice_state (discord.VoiceState | None): Voice state of the user if it's connected to a voice channel if is not it's none.
            song (wavelink.abc.Playable): The song to play.
        
        Raises:
            NotConnectedToVoiceChannelException: if the user is not connected to a voice channel.
        """
        await self.join(voice_state)
        
        self.voice_queues.put_at_front(song)
        if self.voice_clients.is_playing():
            raise AlreadyPlayingException
            
        await self.skip()
            
    async def join(self, voice_state: discord.VoiceState):
        """Connect to the voice channel if the bot is not connected.

        Args:
            voice_state (discord.VoiceState): Voice state of the user if it's connected to a voice channel if is not it's none.

        Raises:
            NotConnectedToVoiceChannelException: if the user is not connected to a voice channel.
            NoPlayingInstanceException: if there is no playing instance.
        """
        if not self.voice_clients:
            if voice_state == None:
                raise NotConnectedToVoiceChannelException
            self.voice_clients = await voice_state.channel.connect(cls=wavelink.Player)
    
    async def skip(self, old_song: wavelink.abc.Playable = None):
        """Skip the current song.

        Args:
            old_song (wavelink.abc.Playable, optional): The old song to put in the back queue. Used for the callback on_wavelink_track_end. Defaults to None. 
        
        Raises:
            NothingLeftInQueueException: if the queue is empty.
            NoPlayingInstanceException: if there is no playing instance.            
        """
        self.__raise_if_there_no_playing_instance()
        
        if self.voice_queues.is_empty:
            raise NothingLeftInQueueException
        
        current_song = self.voice_clients.source
        if current_song != None:
            self.voice_back.put(current_song)
        elif old_song != None:
            self.voice_back.put(old_song)
        
        await self.voice_clients.play(self.voice_queues.pop(), replace=True)
    
    async def back(self):
        """Play the previous song.
        
        Raises:
            NothingLeftInBackQueueException: if the back queue is empty.
            NoPlayingInstanceException: if there is no playing instance.
        """
        self.__raise_if_there_no_playing_instance()
        
        if self.voice_back.is_empty:
            raise NothingLeftInBackQueueException
        
        current_song = self.voice_clients.source
        if current_song != None:
            self.voice_queues.put(current_song)
            
        await self.voice_clients.play(self.voice_back.pop(), replace=True)
    
    async def resume(self):
        """Resume the current song.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """        
        if self.is_paused:
            await self.voice_clients.resume()

    @property
    def is_paused(self) -> bool:
        """Check if the current song is paused.

        Returns:
            bool: True if paused else False.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        self.__raise_if_there_no_playing_instance()
        
        return self.voice_clients.is_paused()
    
    async def search(self, search: str) -> wavelink.abc.Playable:
        """Search a song.

        Args:
            search (str): the string to search on youtube.

        Returns:
            wavelink.abc.Playable: the song to play.
        
        Raises:
            NoResultsFoundException: if there is no results found.
        """
        try: 
            return await wavelink.YouTubeTrack.search(query=search, return_first=True)
        except:
            raise NoResultsFoundException
         
        
    async def stop(self, disconnect: bool = True):
        """Stop the current song.

        Args:
            disconnect (bool, optional): if you need to disconnect the bot after stopping music. Defaults to True.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        self.__raise_if_there_no_playing_instance()
        
        await self.voice_clients.stop()
        if disconnect:
            await self.disconnect()
    
    async def disconnect(self):
        """Disconnect the bot from the voice channel.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        self.__raise_if_there_no_playing_instance()
        
        await self.voice_clients.disconnect()
        self.voice_queues.clear()
        self.voice_back.clear()
        self.voice_clients = None
    
    async def pause(self):
        """Pause the current song.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        if not self.is_paused:
            await self.voice_clients.pause()
    
    @property
    def now(self) -> wavelink.abc.Playable | None:
        """Get the current song.

        Raises:
            NoMusicPlaying: if there is no music playing.
            NoPlayingInstanceException: if there is no playing instance.

        Returns:
            wavelink.abc.Playable | None: the current song.
        """
        self.__raise_if_there_no_playing_instance()
            
        current_music = self.voice_clients.source 
        if current_music is None:
            raise NoMusicPlaying
        return current_music
    
    @property
    def queue(self) -> list[wavelink.abc.Playable]:
        if self.voice_queues.is_empty:
            raise NothingLeftInQueueException
        songs = []
        for song in self.voice_queues:
            songs.append(song)
        return songs
    
    def __raise_if_there_no_playing_instance(self):
        """Raise an exception if there is no playing instance.

        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        if self.voice_clients == None:
            raise NoPlayingInstanceException