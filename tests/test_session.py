"""Tests for session management."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from webterm.core.session import Session, SessionManager


class TestSession:
    """Tests for Session class."""

    def test_session_creation(self):
        """Test creating a session."""
        mock_pty = MagicMock()
        session = Session(id="test-123", pty=mock_pty)

        assert session.id == "test-123"
        assert session.pty == mock_pty
        assert session.created_at is not None
        assert session.last_activity is not None

    def test_session_touch_updates_activity(self):
        """Test that touch() updates last_activity."""
        mock_pty = MagicMock()
        session = Session(id="test-123", pty=mock_pty)

        old_activity = session.last_activity
        # Small delay to ensure time difference
        time.sleep(0.01)
        session.touch()

        assert session.last_activity > old_activity

    def test_session_is_expired(self):
        """Test session expiration check."""
        mock_pty = MagicMock()
        session = Session(id="test-123", pty=mock_pty)

        # Should not be expired immediately
        assert session.is_expired(timeout=3600) is False

        # Manually set last_activity to past
        session.last_activity = time.time() - 7200
        assert session.is_expired(timeout=3600) is True


class TestSessionManager:
    """Tests for SessionManager class."""

    @pytest.fixture
    def manager(self):
        """Create a session manager."""
        return SessionManager(max_sessions=10, session_timeout=3600)

    @pytest.mark.asyncio
    async def test_create_session(self, manager):
        """Test creating a new session."""
        with patch("webterm.core.session.PTYManager") as mock_pty_class:
            mock_pty = MagicMock()
            mock_pty.spawn = AsyncMock(return_value=True)
            mock_pty_class.return_value = mock_pty

            session = await manager.create_session()

            assert session is not None
            assert session.id in manager._sessions
            mock_pty.spawn.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session(self, manager):
        """Test getting an existing session."""
        with patch("webterm.core.session.PTYManager") as mock_pty_class:
            mock_pty = MagicMock()
            mock_pty.spawn = AsyncMock(return_value=True)
            mock_pty_class.return_value = mock_pty

            session = await manager.create_session()
            retrieved = await manager.get_session(session.id)

            assert retrieved == session

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, manager):
        """Test getting a nonexistent session returns None."""
        session = await manager.get_session("nonexistent-id")
        assert session is None

    @pytest.mark.asyncio
    async def test_remove_session(self, manager):
        """Test removing a session."""
        with patch("webterm.core.session.PTYManager") as mock_pty_class:
            mock_pty = MagicMock()
            mock_pty.spawn = AsyncMock(return_value=True)
            mock_pty.terminate = AsyncMock()
            mock_pty_class.return_value = mock_pty

            session = await manager.create_session()
            session_id = session.id

            result = await manager.remove_session(session_id)

            assert result is True
            assert session_id not in manager._sessions
            mock_pty.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_nonexistent_session(self, manager):
        """Test removing a nonexistent session returns False."""
        result = await manager.remove_session("nonexistent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_max_sessions_limit(self, manager):
        """Test that max sessions limit is enforced."""
        manager._max_sessions = 2

        with patch("webterm.core.session.PTYManager") as mock_pty_class:
            mock_pty = MagicMock()
            mock_pty.spawn = AsyncMock(return_value=True)
            mock_pty_class.return_value = mock_pty

            # Create max sessions
            session1 = await manager.create_session()
            session2 = await manager.create_session()

            assert session1 is not None
            assert session2 is not None

            # Third should fail
            session3 = await manager.create_session()
            assert session3 is None

    def test_session_count(self, manager):
        """Test getting session count."""
        assert manager.session_count == 0

    @pytest.mark.asyncio
    async def test_session_count_after_create(self, manager):
        """Test session count increases after creating sessions."""
        with patch("webterm.core.session.PTYManager") as mock_pty_class:
            mock_pty = MagicMock()
            mock_pty.spawn = AsyncMock(return_value=True)
            mock_pty_class.return_value = mock_pty

            await manager.create_session()
            assert manager.session_count == 1

            await manager.create_session()
            assert manager.session_count == 2

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, manager):
        """Test cleaning up expired sessions."""
        with patch("webterm.core.session.PTYManager") as mock_pty_class:
            mock_pty = MagicMock()
            mock_pty.spawn = AsyncMock(return_value=True)
            mock_pty.terminate = AsyncMock()
            mock_pty_class.return_value = mock_pty

            session = await manager.create_session()
            # Set last_activity to past
            session.last_activity = time.time() - 7200
            manager._session_timeout = 3600

            cleaned = await manager.cleanup_expired()

            assert cleaned == 1
            assert manager.session_count == 0
