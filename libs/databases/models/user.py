from MIWOS.model import Model
from MIWOS.libs.sql.association import HasMany, HasAndBelongsToMany


class User(Model):
    _has_many = [HasMany("guildUsers")]
    _has_and_belongs_to_many = [HasAndBelongsToMany("badges", verb="deserve")]

    @classmethod
    def from_discord_id(cls, discord_id: str):
        return cls.whereFirst(discord_id=discord_id)
