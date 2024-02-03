from unittest.mock import patch, Mock, AsyncMock

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import DatabaseSessionManager, sessionmanager
from src.database.fu_db import get_db
from tests.test_configurations import SQLALCHEMY_DATABASE_URL


@pytest.mark.asyncio
async def test_session_manager():
    session_manager = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL)
    async with session_manager.session() as session:
        assert isinstance(session, AsyncSession)
        assert session.is_active
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_session_manager():
    session_manager = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL)
    setattr(session_manager, '_session_maker', None)
    assert session_manager._session_maker is None
    with pytest.raises(Exception, match="Session is not initialized") as exc:
        async with session_manager.session() as session:
            assert isinstance(session, AsyncSession)
    assert "Session is not initialized" in str(exc.value)


@pytest.mark.asyncio
async def test_session_rollback():
    mock_session = Mock()
    session_manager = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL)
    setattr(session_manager, '_session_maker', Mock(return_value=mock_session))
    mock_session.rollback.side_effect = Exception("Some error occurred")
    with pytest.raises(Exception) as exc:
        async with session_manager.session() as session:
            session_manager.execute("SELECT * FROM some_table")
    mock_session.rollback.assert_called_once()
