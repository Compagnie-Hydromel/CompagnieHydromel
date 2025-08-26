from MIWOS.model import Model
from MIWOS.libs.sql.association import BelongsTo


class VoiceChannel(Model):
    _belongs_to = BelongsTo("guild")

    @classmethod
    def from_discord_id(cls, discord_id: str):
        return cls.whereFirst(discord_id=discord_id)
