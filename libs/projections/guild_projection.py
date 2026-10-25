from pydantic import BaseModel

from libs.databases.models.guild import Guild


class GuildProjection(BaseModel):
    id: int
    discord_id: str
    name: str
    icon_url: str

    @classmethod
    def from_guild(cls, guild: Guild):
        return cls(
            id=guild.id,
            discord_id=guild.discord_id,
            name=guild.name,
            icon_url=guild.icon_url,
        )
