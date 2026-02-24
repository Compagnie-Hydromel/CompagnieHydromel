

from pydantic import BaseModel

from libs.databases.models.user import User


class UserProjection(BaseModel):
    id: int
    discord_id: str
    avatar_url: str
    display_name: str
    username: str

    @classmethod
    def from_user(cls, user: User):
        return cls(
            id=user.id,
            discord_id=user.discord_id,
            avatar_url=user.avatar_url,
            display_name=user.display_name,
            username=user.username,
        )
