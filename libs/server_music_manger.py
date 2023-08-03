from libs.music_manager import MusicManager

class ServerMusicManager:
    """Class that manage the music for each server.
    """
    server: dict[int, MusicManager] = {}
    
    def __init__(self) -> None:
        """Constructor of ServerMusicManager class."""
        pass
    
    def get(self, guild_id: int) -> MusicManager:
        """Get the MusicManager for the guild.

        Args:
            guild_id (int): The guild id where we want the MusicManager to play music.

        Returns:
            MusicManager: _description_
        """
        if guild_id not in self.server:
            self.add(guild_id)
        return self.server[guild_id]
    
    def add(self, guild_id: int):
        """Add a MusicManager for the guild.

        Args:
            guild_id (int): The guild id where we want the MusicManager to play music.
        """
        self.server[guild_id] = MusicManager()