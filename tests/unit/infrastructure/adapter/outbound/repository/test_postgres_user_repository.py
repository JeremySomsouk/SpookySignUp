from unittest.mock import MagicMock, patch

import pytest

from src.domain.model import User, Email, ActivationCode
from src.infrastructure.adapter.outbound import PostgresUserRepository
from src.infrastructure.config import DatabaseConfig


@pytest.fixture
def db_config():
    return DatabaseConfig(
        database="test_db",
        user="test_user",
        password="test_password",
        host="localhost",
    )


@pytest.fixture
def user_repository(db_config):
    return PostgresUserRepository(db_config)


def test_save_user(user_repository):
    # Given
    user = User(
        email=Email("test@spookymotion.com"),
        password_hash="hashed_password",
        is_active=False,
        activation_code=ActivationCode(
            value="1234", expires_at=ActivationCode.compute_expiration_datetime()
        ),
    )

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.__enter__.return_value = (
        mock_conn  # Ensure the connection manager returns the mock
    )
    with patch(
            "src.infrastructure.adapter.outbound.repository.postgres_user_repository.psycopg2.connect",
            return_value=mock_conn,
    ):
        # When
        user_repository.save(user)

        # Then
        assert mock_conn.cursor.call_count == 1
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()


def test_find_by_email(user_repository):
    # Given
    email = Email("test@spookymotion.com")
    mock_row = {
        "email": "test@spookymotion.com",
        "password_hash": "hashed_password",
        "is_active": False,
        "activation_code": "1234",
        "code_expires_at": "2025-01-01",
    }

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = mock_row
    mock_cursor.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn

    with patch(
            "src.infrastructure.adapter.outbound.repository.postgres_user_repository.psycopg2.connect",
            return_value=mock_conn,
    ):
        # When
        result = user_repository.find_by_email(email)

        # Then
        assert mock_conn.cursor.call_count == 1
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE email = %s", (email.value,)
        )
        assert isinstance(result, User)
        assert result.email.value == "test@spookymotion.com"
        assert result.password_hash == "hashed_password"
        assert result.is_active is False
        assert result.activation_code.value == "1234"
        assert result.activation_code.expires_at == "2025-01-01"
