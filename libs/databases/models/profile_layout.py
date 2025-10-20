from MIWOS.model import Model

from MIWOS.libs.sql.association import BelongsTo, HasMany

from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout
from libs.databases.models.guild import Guild


class ProfileLayout(Model):
    _has_many = [HasMany("guildusers")]

    @classmethod
    def default(cls):
        return cls(name="default",
                   profil_picture_x=0, profil_picture_y=0,
                   name_x=150, name_y=20,
                   username_x=150, username_y=65,
                   level_x=250, level_y=224,
                   badge_x=150, badge_y=90,
                   level_bar_x=0, level_bar_y=254)

    @classmethod
    def from_name(cls, name: str):
        return cls.whereFirst(name=name)

    @classmethod
    def createFromLayout(cls, name: str, layout: Layout):
        return cls.create(
            name=name,
            profil_picture_x=layout.profile_picture.x,
            profil_picture_y=layout.profile_picture.y,
            name_x=layout.name.x,
            name_y=layout.name.y,
            username_x=layout.username.x,
            username_y=layout.username.y,
            level_x=layout.level.x,
            level_y=layout.level.y,
            badge_x=layout.badge.x,
            badge_y=layout.badge.y,
            level_bar_x=layout.level_bar.x,
            level_bar_y=layout.level_bar.y,
        )

    @property
    def layout(self) -> Layout:
        return Layout(
            Coords(self.profil_picture_x, self.profil_picture_y),
            Coords(self.name_x, self.name_y),
            Coords(self.username_x, self.username_y),
            Coords(self.level_x, self.level_y),
            Coords(self.badge_x, self.badge_y),
            Coords(self.level_bar_x, self.level_bar_y)
        )

    def setLayout(self, layout: Layout):
        self.profil_picture_x = layout.profile_picture.x
        self.profil_picture_y = layout.profile_picture.y
        self.name_x = layout.name.x
        self.name_y = layout.name.y
        self.username_x = layout.username.x
        self.username_y = layout.username.y
        self.level_x = layout.level.x
        self.level_y = layout.level.y
        self.badge_x = layout.badge.x
        self.badge_y = layout.badge.y
        self.level_bar_x = layout.level_bar.x
        self.level_bar_y = layout.level_bar.y
