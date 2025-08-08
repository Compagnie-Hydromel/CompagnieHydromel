from MIWOS.model import Model
from MIWOS.libs.sql.association import HasMany


class Guild(Model):
    _has_many = [HasMany("roles"), HasMany(
        "wallpapers"), HasMany("profileLayouts"), HasMany("guildUsers")]

    @classmethod
    def from_discord_id(cls, discord_id: int):
        return cls.whereFirst(discord_id=discord_id)

    def get_monthly_top_users(self):
        return self.guildUsers.orderBy("monthly_point", "desc").limit(10)

    def get_top_users(self):
        return self.guildUsers.orderBy("level", "desc", "point", "desc").limit(10)

    def get_most_smart_users(self):
        return self.guildUsers.orderBy("smartpoint", "desc").limit(10)
