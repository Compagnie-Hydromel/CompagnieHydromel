from MIWOS.model import Model

from MIWOS.libs.sql.association import HasAndBelongsToMany, BelongsTo

from libs.databases.models.guild import Guild


class Wallpaper(Model):
    _belongs_to = [BelongsTo("guild")]
    _has_and_belongs_to_many = [HasAndBelongsToMany("guildusers", verb="buy")]

    @classmethod
    def default(cls):
        return cls(name="default",
                   url="https://shkermit.ch/~ethann/compHydromel/wallpapers/default.png")

    @classmethod
    def from_name(cls, name: str):
        return cls.whereFirst(name=name)

    @classmethod
    def from_guild_and_name(cls, guild_id: int, name: str):
        guild = Guild.from_discord_id(guild_id)
        if guild is None:
            return None

        wallpaper = guild.wallpapers.where(name=name).limit(1)

        if len(wallpaper) == 0:
            return None

        return wallpaper[0]
