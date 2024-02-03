from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from src.models.models import User
from tests.test_configurations import TestingSessionLocal
from tests.test_auth import user_data


@pytest.mark.asyncio
async def test_create_contact(client, monkeypatch):
    # Test case 1: Creating a contact with valid data
    # Expected: The contact is created and the response status code is 201
    body = {
        "name": "Valera",
        "surname": "Lazybones",
        "email": "Lazyval@example.com",
        "number": "1234567890",
        "birthday": "1992-05-07",
        "description": "Test contact"
    }
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.is_verified = True
            await session.commit()

    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    response = client.post("api/address_book/", json=body)
    assert response.status_code == 201
    assert response.json()["name"] == body["name"]
    assert response.json()["surname"] == body["surname"]
    assert response.json()["email"] == body["email"]
    assert response.json()["number"] == body["number"]
    assert response.json()["birthday"] == body["birthday"]
    assert response.json()["description"] == body["description"]

    # Test case 2: Creating a contact with invalid data
    # Expected: The contact creation fails


    # Test case 3: Creating a contact with missing required fields
    # Expected: The contact creation fails
    ...

    # Test case 4: Creating a contact without a valid user
    # Expected: The contact creation fails
    ...

    # Test case 5: Creating a contact with rate limiting exceeded
    # Expected: The contact creation fails
    ...


def test_get_contacts():
    assert False


def test_get_contact():
    assert False


def test_update_contact():
    assert False


def test_delete_contact():
    assert False
