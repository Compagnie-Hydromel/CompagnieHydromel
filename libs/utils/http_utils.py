from fastapi import HTTPException, Request

from libs.databases.models.user import User


class HTTPUtils:
    @staticmethod
    def get_user_from_session(request: Request) -> User:
        user = User.find(request.session.get("user_id", None))
        if not user:
            raise HTTPException(
                status_code=401, detail="No active session found.")
        return user
