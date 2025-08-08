from MIWOS.model import Model

from MIWOS.libs.sql.association import HasAndBelongsToMany, BelongsTo


class Wallpaper(Model):
    _belongs_to = [BelongsTo("guild")]
    _has_and_belongs_to_many = [HasAndBelongsToMany("guildUsers", verb="buy")]
