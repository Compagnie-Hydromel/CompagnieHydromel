from libs.music.music_manager import MusicManager
from libs.communication.live import notify_change


class GuildMusicManager:
    def __init__(self):
        self.guild = {}

    def get(self, guild_id: int) -> MusicManager:
        if guild_id not in self.guild:
            self.guild[guild_id] = MusicManager()
            self.guild[guild_id].on_change = lambda: notify_change(
                guild_id, "music")
        return self.guild[guild_id]
