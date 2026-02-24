from pydantic import BaseModel

from libs.databases.models.guild_user import GuildUser
from libs.databases.models.wallpaper import Wallpaper
from libs.projections.wallpaper_projection import WallpaperProjection


class GuildUserProjection(BaseModel):
    id: int
    monthly_point: int
    level: int
    smartpoint: int
    progress: float
    wallpaper: WallpaperProjection
    badges: list
    bar_color: str
    name_color: str
    avatar_url: str
    display_name: str
    username: str

    @classmethod
    def from_guild_user(cls, guild_user: GuildUser):
        wallpaper = guild_user.wallpaper
        return cls(
            id=guild_user.id,
            monthly_point=guild_user.monthly_point,
            level=guild_user.level,
            smartpoint=guild_user.smartpoint,
            progress=guild_user.progress(),
            wallpaper=WallpaperProjection.from_wallpaper(
                wallpaper) if wallpaper else WallpaperProjection.from_wallpaper(Wallpaper.default()),
            badges=[badge.url for badge in guild_user.user.badges],
            bar_color=guild_user.bar_color,
            name_color=guild_user.name_color,
            avatar_url=guild_user.avatar_url,
            display_name=guild_user.display_name,
            username=guild_user.username
        )
