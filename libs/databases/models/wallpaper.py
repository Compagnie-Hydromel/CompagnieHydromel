from MIWOS.model import Model

from MIWOS.libs.sql.association import HasAndBelongsToMany, BelongsTo


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
