import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from fastapi_users.jwt import generate_jwt
from fastapi_users.password import PasswordHelper
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.models.models import Base, User
from src.database.fu_db import get_db
from src.conf.config import config

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {"username": "godzilla", "email": "godzilla@test.io",
             "password": "12345678", "token_audience": "fastapi-users:verify"}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = PasswordHelper().hash(test_user["password"])
            current_user = User(username=test_user["username"], email=test_user["email"], hashed_password=hash_password,
                                is_active=True, is_verified=False, is_superuser=True)
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = generate_jwt({"sub": '1', "email": test_user["email"], "aud": test_user["token_audience"]},
                         config.SECRET_KEY_JWT)
    return token
