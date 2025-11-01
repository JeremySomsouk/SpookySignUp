from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from src.application.service.activate_user_service import ActivateUserService
from src.domain.exception import (
    InvalidActivationCodeException,
    ExpiredActivationCodeException,
    UserAlreadyActiveException,
    UserNotFoundException,
)
from src.domain.model import User, Email, ActivationCode
from src.domain.port import UserRepositoryPort


class TestActivateUserService:
    """Unit tests for ActivateUserService"""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository"""
        return MagicMock(spec=UserRepositoryPort)

    @pytest.fixture
    def activate_user_service(self, mock_user_repository):
        """Create an instance of ActivateUserService with mocked repository"""
        return ActivateUserService(mock_user_repository)

    @pytest.fixture
    def test_user(self):
        """Create a test user with activation code"""
        return User(
            email=Email("test@spookymotion.com"),
            password_hash="hashed_password",
            is_active=False,
            activation_code=ActivationCode(
                value="1234", expires_at=ActivationCode.compute_expiration_datetime()
            ),
        )

    def test_activate_user_success(
            self, activate_user_service, mock_user_repository, test_user
    ):
        """Should successfully activate a user with correct code"""
        # Given
        mock_user_repository.find_by_email.return_value = test_user

        # When
        result = activate_user_service.activate_user("test@spookymotion.com", "1234")

        # Then
        assert result == test_user
        assert result.is_active is True
        assert result.activation_code is None
        mock_user_repository.find_by_email.assert_called_once_with(
            Email("test@spookymotion.com")
        )
        mock_user_repository.save.assert_called_once_with(test_user)

    def test_activate_user_with_wrong_code(
            self, activate_user_service, mock_user_repository, test_user
    ):
        """Should raise InvalidActivationCodeException when activation code is wrong"""
        # Given
        mock_user_repository.find_by_email.return_value = test_user

        # When/Then
        with pytest.raises(InvalidActivationCodeException) as exception:
            activate_user_service.activate_user("test@spookymotion.com", "0000")
        assert "Invalid activation code" in str(exception.value)
        mock_user_repository.find_by_email.assert_called_once_with(
            Email("test@spookymotion.com")
        )
        mock_user_repository.save.assert_not_called()

    def test_activate_user_with_expired_code(
            self, activate_user_service, mock_user_repository, test_user
    ):
        """Should raise ExpiredActivationCodeException when activation code is expired"""
        # Given
        test_user.activation_code = ActivationCode(
            value="1234",
            expires_at=ActivationCode.compute_expiration_datetime() - timedelta(days=1),
        )
        mock_user_repository.find_by_email.return_value = test_user

        # When/Then
        with pytest.raises(ExpiredActivationCodeException) as exception:
            activate_user_service.activate_user("test@spookymotion.com", "1234")
        assert "Activation code has expired" in str(exception.value)
        mock_user_repository.find_by_email.assert_called_once_with(
            Email("test@spookymotion.com")
        )
        mock_user_repository.save.assert_not_called()

    def test_activate_user_not_found(self, activate_user_service, mock_user_repository):
        """Should raise UserNotFoundException when user is not found"""
        # Given
        mock_user_repository.find_by_email.return_value = None

        # When/Then
        with pytest.raises(UserNotFoundException) as exception:
            activate_user_service.activate_user("nonexistent@spookymotion.com", "1234")
        assert "No user found with email: nonexistent@spookymotion.com" in str(
            exception.value
        )
        mock_user_repository.find_by_email.assert_called_once_with(
            Email("nonexistent@spookymotion.com")
        )
        mock_user_repository.save.assert_not_called()

    def test_activate_already_active_user(
            self, activate_user_service, mock_user_repository, test_user
    ):
        """Should raise ValueError when trying to activate an already active user"""
        # Given
        test_user.is_active = True
        test_user.activation_code = None
        mock_user_repository.find_by_email.return_value = test_user

        # When/Then
        with pytest.raises(UserAlreadyActiveException) as exception:
            activate_user_service.activate_user("test@spookymotion.com", "1234")
        assert "User (test@spookymotion.com) already active" in str(exception.value)
        mock_user_repository.find_by_email.assert_called_once_with(
            Email("test@spookymotion.com")
        )
        mock_user_repository.save.assert_not_called()

    def test_activate_user_with_null_activation_code(
            self, activate_user_service, mock_user_repository, test_user
    ):
        """Should raise ValueError when user has no activation code"""
        # Given
        test_user.activation_code = None
        mock_user_repository.find_by_email.return_value = test_user

        # When/Then
        with pytest.raises(ValueError) as exception:
            activate_user_service.activate_user("test@spookymotion.com", "1234")
        assert "No activation code set" in str(exception.value)
        mock_user_repository.find_by_email.assert_called_once_with(
            Email("test@spookymotion.com")
        )
        mock_user_repository.save.assert_not_called()

    def test_activate_user_repository_save_failure(
            self, activate_user_service, mock_user_repository, test_user
    ):
        """Should propagate exceptions when repository save fails"""
        # Given
        mock_user_repository.find_by_email.return_value = test_user
        mock_user_repository.save.side_effect = RuntimeError("Database error")

        # When/Then
        with pytest.raises(RuntimeError) as exception:
            activate_user_service.activate_user("test@spookymotion.com", "1234")
        assert "Database error" in str(exception.value)
        mock_user_repository.find_by_email.assert_called_once_with(
            Email("test@spookymotion.com")
        )
        mock_user_repository.save.assert_called_once_with(test_user)
