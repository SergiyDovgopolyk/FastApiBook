import uuid

from datetime import datetime
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str
    avatar: str
    refresh_token: str | None
    created_at: datetime
    updated_at: datetime


class UserCreate(schemas.BaseUserCreate):
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str
    avatar: str
    refresh_token: str
