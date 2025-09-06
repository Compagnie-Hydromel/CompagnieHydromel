from MIWOS.model import Model
from MIWOS.libs.sql.association import BelongsTo, HasAndBelongsToMany

from libs.databases.models.guild import Guild
from libs.databases.models.user import User
from libs.exception.bot_exception import BotException
from libs.utils.utils import Utils


class GuildUser(Model):
    _belongs_to = [BelongsTo("guild"), BelongsTo("user"),
                   BelongsTo("wallpaper"), BelongsTo("profilelayout")]
    _has_and_belongs_to_many = [HasAndBelongsToMany("wallpapers", verb="buy")]
    _validators = {
        "smartpoint": lambda value: value >= 0,
    }
    _default_attributes = {
        "point": 0,
        "monthly_point": 0,
        "level": 1,
        "smartpoint": 20,
        "bar_color": "#ADFF2F",
        "name_color": "#0000FF",
        "has_accepted_rules": False,
        "is_admin": False
    }

    @classmethod
    def from_user_and_guild(cls, user: User, guild: Guild):
        guilduser = cls.whereFirst(
            user=user,
            guild=guild
        )
        if guilduser is None:
            guilduser = cls(user=user, guild=guild)
            guilduser.save()
        return guilduser

    @classmethod
    def from_user_discord_id_and_guild_discord_id(cls, discord_id: str, guild_id: str):
        user = User.from_discord_id(discord_id)
        guild = Guild.from_discord_id(guild_id)

        return cls.from_user_and_guild(user, guild)

    @property
    def name_color(self) -> str:
        return f"#{super().name_color.lstrip('#')}"

    @property
    def bar_color(self) -> str:
        return f"#{self._bar_color.lstrip('#')}"

    def beforeValidation(self):
        if self.isDirty("name_color"):
            self.name_color = Utils.check_color(self.name_color)
        if self.isDirty("bar_color"):
            self.bar_color = Utils.check_color(self.bar_color)
        if self.isDirty("wallpaper"):
            if self.wallpaper not in self.wallpapers and self.wallpaper is not None:
                raise YouDontOwnThisWallpaperException()

    def beforeSave(self):
        if self.isDirty("point"):
            point = self.point
            level = self.level
            calculated_point_per_level = 200 * level
            calculated_money_per_level = 100+(level*100)
            if level > 15:
                calculated_point_per_level = 200 * 15
                calculated_money_per_level = 100+(15*100)

            if point >= calculated_point_per_level:
                self.level += 1
                self.point = 0
                self.smartpoint += calculated_money_per_level
                self.__check_add_if_wallpaper_at_this_level()

    def __check_add_if_wallpaper_at_this_level(self) -> None:
        """This method is designed to check if the user can add a wallpaper at this level.
        """
        for wallpaper in self.guild.wallpapers:
            if wallpaper.level == self.level:
                try:
                    self.wallpapers.append(wallpaper)
                except:
                    pass


class YouDontOwnThisWallpaperException(BotException):
    def __init__(self):
        super().__init__("You don't own this wallpaper.")
