from MIWOS.model import Model
from MIWOS.libs.sql.association import BelongsTo

from libs.databases.models.guild import Guild


class Role(Model):
    _belongs_to = [BelongsTo("guild")]
    _validators = {
        "level": lambda value: value >= 1,
    }

    @classmethod
    def from_discord_id(cls, discord_id: str) -> "Role|None":
        return cls.whereFirst(discord_id=discord_id)

    @classmethod
    def by_level_and_guild(cls, level: int, guild: Guild) -> "Role|None":
        return cls.whereFirst(level=level, guild=guild)

    @classmethod
    def by_level_and_guild_discord_id(cls, level: int, guild_discord_id: int) -> "Role|None":
        guild = Guild.from_discord_id(guild_discord_id)
        if not guild:
            return None

        return cls.by_level_and_guild(level, guild)
