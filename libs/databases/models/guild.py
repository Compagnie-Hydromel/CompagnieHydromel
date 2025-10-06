from MIWOS.libs.sql.association import HasMany

from libs.databases.models.application_model import ApplicationModel


class Guild(ApplicationModel):
    _has_many = [HasMany("roles"), HasMany(
        "wallpapers"), HasMany("guildusers"), HasMany("voicechannels")]
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

    def get_guild(self):
        return self.get_bot().get_guild(int(self.discord_id))

    @property
    def name(self):
        return self.get_guild().name

    @property
    def icon_url(self):
        return self.get_guild().icon.url

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["name"] = self.name
        base_dict["icon_url"] = self.icon_url
        return base_dict
