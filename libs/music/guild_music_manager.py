from libs.music.music_manager import MusicManager


class GuildMusicManager:
    def __init__(self):
        self.guild = {}

    def get(self, guild_id: int) -> MusicManager:
        if guild_id not in self.guild:
            self.guild[guild_id] = MusicManager()
        return self.guild[guild_id]
