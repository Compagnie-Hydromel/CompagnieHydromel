from MIWOS.model import Model
from MIWOS.libs.sql.association import HasMany


class Guild(Model):
    _has_many = [HasMany("roles"), HasMany(
        "wallpapers"), HasMany("guildusers")]
    _default_attributes = {
        "information_channel_id": "0",
        "monthlytop_channel_id": "0"
    }

    @classmethod
    def from_discord_id(cls, discord_id: int):
        guild = cls.whereFirst(discord_id=discord_id)
        if guild is None:
            guild = cls(discord_id=discord_id)
            guild.save()
        return guild

    def get_monthly_top_users(self):
        return self.guildusers.orderBy("monthly_point DESC").limit(10)

    def get_top_users(self):
        return self.guildusers.orderBy("level DESC", "point DESC").limit(10)

    def get_most_smart_users(self):
        return self.guildusers.orderBy("smartpoint DESC").limit(10)
