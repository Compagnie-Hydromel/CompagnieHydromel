import wavelink
from libs.music.music_manager import MusicManager

class GuildMusicManager:
    """Class that manage the music for each guild.
    """
    guild: dict[int, MusicManager] = {}
    
    def __init__(self, node: wavelink.Node) -> None:
        """Constructor of GuildMusicManager class."""
        self.__node = node 
    
    def get(self, guild_id: int) -> MusicManager:
        """Get the MusicManager for the guild.

        Args:
            guild_id (int): The guild id where we want the MusicManager to play music.

        Returns:
            MusicManager: _description_
        """
        if guild_id not in self.guild:
            self.add(guild_id)
        return self.guild[guild_id]
    
    def add(self, guild_id: int):
        """Add a MusicManager for the guild.

        Args:
            guild_id (int): The guild id where we want the MusicManager to play music.
        """
        self.guild[guild_id] = MusicManager(self.__node)