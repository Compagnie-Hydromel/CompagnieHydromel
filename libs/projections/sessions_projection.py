from pydantic import BaseModel

from libs.projections.user_projection import UserProjection


class SessionsProjection(BaseModel):
    user: UserProjection
