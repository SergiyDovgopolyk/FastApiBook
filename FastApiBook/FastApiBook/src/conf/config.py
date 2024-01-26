from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:14021992@localhost:5432/rest_app"
    SECRET_KEY_JWT: str = "secret_jwt"
    MAIL_USERNAME: EmailStr = "postgres@email.com"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM: str = "username@email.com"
    MAIL_PORT: int = 000
    MAIL_SERVER: str = "email_server"
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 0000
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = 'abc'
    CLD_API_KEY: int = 000000000000000
    CLD_API_SECRET: str = "secret"


    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
