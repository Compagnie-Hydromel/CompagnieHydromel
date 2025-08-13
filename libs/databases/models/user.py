from MIWOS.model import Model
from MIWOS.libs.sql.association import HasMany, HasAndBelongsToMany


class User(Model):
    _has_many = [HasMany("guildusers")]
    _has_and_belongs_to_many = [HasAndBelongsToMany("badges", verb="deserve")]

    @classmethod
    def from_discord_id(cls, discord_id: str):
        user = cls.whereFirst(discord_id=discord_id)
        if user is None:
            user = cls(discord_id=discord_id)
            user.save()
        return user
