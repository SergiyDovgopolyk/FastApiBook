import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import User
from src.repository.users import update_avatar_url


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(
            id=1,
            username="test_user",
            avatar="test_avatar",
            refresh_token="test_refresh_token",
            is_verified=True
        )
        self.session = AsyncMock(spec=AsyncSession)

    def tearDown(self):
        self.user = None
        self.session = None

    async def test_update_avatar_url(self):
        url = "test_url"
        result = await update_avatar_url(self.user, url, self.session)
        self.assertEqual(result.avatar, url)
        self.session.commit.assert_called_once()
