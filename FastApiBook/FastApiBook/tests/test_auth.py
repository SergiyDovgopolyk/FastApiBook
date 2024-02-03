from unittest.mock import Mock, patch

import pytest
from fastapi_users.router import ErrorCode
from fastapi_users.router.common import ErrorModel
from sqlalchemy import select

from src.entity.models import User
from src.services.auth import UserManager
from tests.conftest import TestingSessionLocal

user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678"}


def test_signup(client, monkeypatch, get_token):
    with patch.object(UserManager, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        mock_send_email = Mock()
        monkeypatch.setattr("src.services.email.send_email_verification", mock_send_email)
        response = client.post("auth/register", json=user_data)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "hashed_password" not in data
        assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.services.email.send_email_verification", mock_send_email)
    response = client.post("auth/register", json=user_data)
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == ErrorCode.REGISTER_USER_ALREADY_EXISTS



def test_not_confirmed_login(client):
    response = client.post(
        "auth/jwt/login", data={"username": user_data.get("email"), "password": user_data.get("password")}
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == ErrorCode.LOGIN_USER_NOT_VERIFIED


@pytest.mark.asyncio
async def test_login(client, monkeypatch):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.is_verified = True
            await session.commit()

    with patch.object(UserManager, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        mock_send_email = Mock()
        monkeypatch.setattr("src.services.email.send_email_verification", mock_send_email)
        response = client.post(
            "auth/jwt/login", data={"username": user_data.get("email"), "password": user_data.get("password")})
        assert response.status_code == 200, response.text
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "auth/jwt/login", data={"username": user_data.get("email"), "password": "password"})
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS


def test_wrong_email_login(client):
    response = client.post(
        "auth/jwt/login", data={"username": "email", "password": user_data.get("password")})
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == ErrorCode.LOGIN_BAD_CREDENTIALS


def test_validation_error_login(client):
    response = client.post("auth/jwt/login", data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_bad_confirmed_email(client, get_token):
    wrong_token = "invalid_token"
    response = client.get(f"auth/confirmed_email/{wrong_token}")
    assert response.status_code == 400
    error = ErrorModel(**response.json())
    assert error.detail == ErrorCode.VERIFY_USER_BAD_TOKEN
