import traceback
import discord
import wavelink
from libs.exception.music.already_playing_exception import AlreadyPlayingException
from libs.exception.music.no_music_playing_exception import NoMusicPlayingException
from libs.exception.music.no_playing_instance_exception import NoPlayingInstanceException
from libs.exception.music.no_result_found_exception import NoResultsFoundException

from libs.exception.music.not_connected_to_voice_channel_exception import NotConnectedToVoiceChannelException
from libs.exception.music.nothing_left_in_back_queue import NothingLeftInBackQueueException
from libs.exception.music.nothing_left_in_queue_exception import NothingLeftInQueueException
from libs.log import Log

class MusicManager:
    """Class that manage the music.
    """
    def __init__(self, node: wavelink.Node) -> None:
        """Constructor of MusicManager class.
        """
        self.voice_clients: wavelink.Player = None
        self.back_queue: wavelink.Queue = wavelink.Queue()
        node.client.add_listener(self.on_track_end, "on_wavelink_track_end")
        self.__node = node

    async def on_track_end(self, payload: wavelink.TrackEndEventPayload):
        """Event that is called when the track ends.
        
        Args:
            payload (wavelink.TrackEndEventPayload): The payload of the event.
        """
        match(payload.reason):
            case "finished":
                Log.info("Track end with reason: " + payload.reason)

                try: 
                    await self.skip()
                    self.back_queue.put_at(0, payload.track)
                except NoPlayingInstanceException:
                    Log.info("No playing instance")
                    await self.disconnect()
                    return
                except NothingLeftInQueueException:
                    Log.info("Queue is empty")
                    await self.disconnect()
                    return
                except Exception as e:
                    Log.error("An error occurred: " + traceback.format_exc())
            case "stopped":
                pass
            case _:
                Log.warning("Track end with reason: " + payload.reason)
    
    
    async def play(self, voice_state: discord.VoiceState | None, song: wavelink.Playable):        
        """Play a song.

        Args:
            voice_state (discord.VoiceState | None): Voice state of the user if it's connected to a voice channel if is not it's none.
            song (wavelink.Playable): The song to play.
        
        Raises:
            NotConnectedToVoiceChannelException: if the user is not connected to a voice channel.
        """
        await self.join(voice_state)

        if self.voice_clients.playing:
            self.voice_clients.auto_queue.put(song)
            raise AlreadyPlayingException
        
        await self.voice_clients.play(song)
        Log.info("Playing " + str(song) + " / " + str(song.uri) + " in " + self.voice_clients.channel.name)
        self.voice_clients.autoplay = wavelink.AutoPlayMode.disabled # partial auto play mode isn't working
            
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
            Log.info("Connecting to " + voice_state.channel.name + " | " + str(voice_state.channel.id))
            self.voice_clients = await voice_state.channel.connect(cls=wavelink.Player)

    async def skip(self):
        """Skip the current song.

        Raises:
            NothingLeftInQueueException: if the queue is empty.
            NoPlayingInstanceException: if there is no playing instance.            
        """
        self.__raise_if_there_no_playing_instance()

        if self.voice_clients.auto_queue.is_empty:
            raise NothingLeftInQueueException
        if self.voice_clients.playing:
            last_song = await self.voice_clients.stop()
            self.back_queue.put_at(0, last_song)

        song = await self.voice_clients.play(self.voice_clients.auto_queue.get())
        self.voice_clients.auto_queue.remove(song)

        Log.info("Playing " + str(song) + " / " + str(song.uri) + " in " + self.voice_clients.channel.name)

        await self.resume()

    async def back(self):
        """Play the previous song.
        
        Raises:
            NothingLeftInBackQueueException: if the back queue is empty.
            NoPlayingInstanceException: if there is no playing instance.
        """
        self.__raise_if_there_no_playing_instance()
        
        if self.back_queue.is_empty:
            raise NothingLeftInBackQueueException
        
        current_song = self.voice_clients.current
        if current_song != None:
            self.voice_clients.auto_queue.put_at(0, current_song)

        song = self.back_queue.get()
        self.back_queue.remove(song)

        Log.info("Playing " + str(song) + " / " + str(song.uri) + " in " + self.voice_clients.channel.name)

        await self.voice_clients.stop()
        await self.voice_clients.play(song)

        await self.resume()
    
    async def resume(self):
        """Resume the current song.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """        
        if self.is_paused:
            Log.info("Resuming music in " + self.voice_clients.channel.name)
            await self.voice_clients.pause(False)

    @property
    def is_paused(self) -> bool:
        """Check if the current song is paused.

        Returns:
            bool: True if paused else False.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        self.__raise_if_there_no_playing_instance()
        
        return self.voice_clients.paused
    
    async def search(self, search: str) -> wavelink.Playable:
        """Search a song.

        Args:
            search (str): the string to search on youtube.

        Returns:
            wavelink.Playable: the song to play.
        
        Raises:
            NoResultsFoundException: if there is no results found.
        """
        music_list: list[wavelink.Playable] = await wavelink.Playable.search(search, node = self.__node)

        if type(music_list) == wavelink.Playlist:
            music_list_playlist : wavelink.Playlist = music_list
            return music_list_playlist.pop()

        if len(music_list) == 0:
            raise NoResultsFoundException

        return music_list[0]
         
        
    async def stop(self, disconnect: bool = True):
        """Stop the current song.

        Args:
            disconnect (bool, optional): if you need to disconnect the bot after stopping music. Defaults to True.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        self.__raise_if_there_no_playing_instance()
        
        Log.info("Stopping music in " + self.voice_clients.channel.name)
        await self.voice_clients.stop()
        if disconnect:
            Log.info("Disconnect from " + self.voice_clients.channel.name)
            await self.disconnect()
    
    async def disconnect(self):
        """Disconnect the bot from the voice channel.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        self.__raise_if_there_no_playing_instance()
        
        Log.info("Disconnect from " + self.voice_clients.channel.name)
        await self.voice_clients.disconnect()
        self.voice_clients = None
    
    async def pause(self):
        """Pause the current song.
        
        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        if not self.is_paused:
            Log.info("Pausing music in " + self.voice_clients.channel.name)
            await self.voice_clients.pause(True)
    
    @property
    def now(self) -> wavelink.Playable | None:
        """Get the current song.

        Raises:
            NoMusicPlayingException: if there is no music playing.
            NoPlayingInstanceException: if there is no playing instance.

        Returns:
            wavelink.Playable | None: the current song.
        """
        self.__raise_if_there_no_playing_instance()
            
        current_music = self.voice_clients.current 
        if current_music is None:
            raise NoMusicPlayingException
        return current_music
    
    @property
    def queue(self) -> list[wavelink.Playable]:
        """Get the queue.

        Raises:
            NothingLeftInQueueException: if the queue is empty.

        Returns:
            list[wavelink.Playable]: the queue.
        """
        if self.voice_clients is None:
            raise NothingLeftInQueueException
        if self.voice_clients.auto_queue.is_empty:
            raise NothingLeftInQueueException
        songs = []
        for song in reversed(self.voice_clients.auto_queue):
            songs.append(song)
        return songs
    
    def __raise_if_there_no_playing_instance(self):
        """Raise an exception if there is no playing instance.

        Raises:
            NoPlayingInstanceException: if there is no playing instance.
        """
        if self.voice_clients == None:
            raise NoPlayingInstanceException