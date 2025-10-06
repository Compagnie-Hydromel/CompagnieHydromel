import os
from MIWOS.libs.sql.association import HasMany, HasAndBelongsToMany
import jwt
from datetime import datetime, timedelta

from libs.databases.models.application_model import ApplicationModel


class User(ApplicationModel):
    _has_many = [HasMany("guildusers")]
    _has_and_belongs_to_many = [HasAndBelongsToMany("badges", verb="deserve")]

    @classmethod
    def from_discord_id(cls, discord_id: str):
        user = cls.whereFirst(discord_id=discord_id)
        if user is None:
            user = cls(discord_id=discord_id)
            user.save()
        return user

    def generate_authorization_token(self):
        jwt_secret = os.getenv("SESSION_SECRET_KEY", "supersecretkey")
        expiration = datetime.now() + timedelta(minutes=1)
        payload = {"user_id": self.id, "expiration": expiration.timestamp()}
        return jwt.encode(payload, jwt_secret, algorithm="HS256")

    @classmethod
    def verify_authorization_token(cls, token: str):
        jwt_secret = os.getenv("SESSION_SECRET_KEY", "supersecretkey")
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            if "expiration" in payload and datetime.now() > datetime.fromtimestamp(payload["expiration"]):
                return None
            return cls.find(payload.get("user_id"))
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def get_user(self):
        return self.get_bot().get_user(int(self.discord_id))

    @property
    def avatar_url(self):
        return self.get_user().avatar.url

    @property
    def display_name(self):
        return self.get_user().display_name

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["avatar_url"] = self.avatar_url
        base_dict["display_name"] = self.display_name
        return base_dict
