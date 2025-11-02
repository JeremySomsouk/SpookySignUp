import uuid
from unittest.mock import MagicMock

import pytest

from src.application.service.register_user_service import RegisterUserService
from src.domain.exception import EmailAlreadyExistsException
from src.domain.model import User, Email, ActivationCode
from src.domain.port import UserRepositoryPort, EmailSenderPort


class TestRegisterUserService:
    """Unit tests for RegisterUserService"""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository"""
        return MagicMock(spec=UserRepositoryPort)

    @pytest.fixture
    def mock_email_sender(self):
        """Create a mock email sender"""
        return MagicMock(spec=EmailSenderPort)

    @pytest.fixture
    def register_user_service(self, mock_user_repository, mock_email_sender):
        """Create an instance of RegisterUserService with mocked dependencies"""
        return RegisterUserService(mock_user_repository, mock_email_sender)

    @pytest.fixture
    def test_user(self):
        """Create a test user with hashed password"""
        return User(
            id=uuid.uuid4(),
            email=Email("test@spookymotion.com"),
            password_hash="hashed_password_123",
            is_active=False,
            activation_code=ActivationCode(
                value="1234", expires_at=ActivationCode.compute_expiration_datetime()
            ),
        )

    def test_register_user_success(
        self, register_user_service, mock_user_repository, mock_email_sender
    ):
        """Should successfully register a new user"""
        # Given
        mock_user_repository.find_by_email.return_value = None

        # When
        result = register_user_service.register_user(
            "test@spookymotion.com", "password123"
        )

        # Then
        assert result.email.value == "test@spookymotion.com"
        assert result.is_active is False
        assert result.activation_code.value is not None
        mock_user_repository.find_by_email.assert_called_once_with(
            Email("test@spookymotion.com")
        )
        mock_user_repository.save.assert_called_once()
        mock_email_sender.send_activation_email.assert_called_once_with(
            Email("test@spookymotion.com"), result.activation_code.value
        )

    def test_register_user_with_existing_email(
        self, register_user_service, mock_user_repository, test_user, mock_email_sender
    ):
        """Should raise EmailAlreadyExistsException when email already exists"""
        # Given
        mock_user_repository.find_by_email.return_value = test_user

        # When/Then
        with pytest.raises(EmailAlreadyExistsException) as exception:
            register_user_service.register_user("test@spookymotion.com", "password123")
        assert (
            "email test@spookymotion.com already registered"
            in str(exception.value).lower()
        )
        mock_user_repository.find_by_email.assert_called_once_with(
            Email("test@spookymotion.com")
        )
        mock_user_repository.save.assert_not_called()
        mock_email_sender.send_activation_email.assert_not_called()

    def test_register_user_with_invalid_email(
        self, register_user_service, mock_user_repository, mock_email_sender
    ):
        """Should raise ValueError when email is invalid"""
        # When/Then
        with pytest.raises(ValueError) as exception:
            register_user_service.register_user("invalid-email", "password123")
        assert "invalid email" in str(exception.value).lower()
        mock_user_repository.find_by_email.assert_not_called()
        mock_user_repository.save.assert_not_called()
        mock_email_sender.send_activation_email.assert_not_called()
