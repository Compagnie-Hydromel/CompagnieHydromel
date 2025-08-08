from MIWOS.model import Model
from MIWOS.libs.sql.association import BelongsTo


class Role(Model):
    _belongs_to = [BelongsTo("guild")]

    @classmethod
    def from_discord_id(cls, discord_id: str) -> "Role|None":
        return cls.whereFirst("discord_id", discord_id)

    @classmethod
    def by_level(cls, level: int) -> "Role|None":
        return cls.whereFirst("level", level)
