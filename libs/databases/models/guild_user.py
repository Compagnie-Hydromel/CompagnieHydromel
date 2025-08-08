from MIWOS.model import Model
from MIWOS.libs.sql.association import BelongsTo, HasAndBelongsToMany

from libs.databases.models.user import User
from libs.databases.models.wallpaper import Wallpaper
from libs.exception.smartpoint.not_enougt_smartpoint_exception import NotEnougtSmartpointException


class GuildUser(Model):
    table_name = "guild_users"
    _belongs_to = [BelongsTo("guild"), BelongsTo("user"),
                   BelongsTo("wallpaper"), BelongsTo("profileLayout")]
    _has_and_belongs_to_many = [HasAndBelongsToMany("wallpapers", verb="buy")]

    @classmethod
    def from_user_and_guild_id(cls, user: User, guild_id: str):
        return cls.whereFirst(
            user_id=user.id,
            guild_id=guild_id
        )

    @classmethod
    def from_discord_id_and_guild_id(cls, discord_id: str, guild_id: str):
        user = User.from_discord_id(discord_id)

        return cls.from_user_and_guild_id(user, guild_id)

    @property
    def smartpoint(self) -> int:
        return super().smartpoint

    @smartpoint.setter
    def smartpoint(self, value: int):
        if self.smartpoint + value < 0:
            raise NotEnougtSmartpointException()
        super().smartpoint = value

    @property
    def point(self) -> int:
        return super().point

    @point.setter
    def point(self, value: int):
        super().point += value

        point = self.point
        level = self.level
        calculated_point_per_level = 200 * level
        calculated_money_per_level = 100+(level*100)
        if level > 15:
            calculated_point_per_level = 200 * 15
            calculated_money_per_level = 100+(15*100)

        if point >= calculated_point_per_level:
            self.level += 1
            super().point = 0
            self.smartpoint += calculated_money_per_level
            self.__check_add_if_wallpaper_at_this_level()

    def __check_add_if_wallpaper_at_this_level(self) -> None:
        """This method is designed to check if the user can add a wallpaper at this level.
        """
        for wallpaper in Wallpaper.all():
            if wallpaper.level == self.level:
                try:
                    self.wallpapers.append(wallpaper)
                except:
                    pass
