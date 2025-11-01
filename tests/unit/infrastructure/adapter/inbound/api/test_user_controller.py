from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status

from src.application.dto.request import ActivateUserRequest, RegisterUserRequest
from src.application.service import ActivateUserService
from src.domain.model import User, Email
from src.infrastructure.adapter.inbound.api import register_user, activate_user


class TestUserController:
    @patch("src.infrastructure.dependencies.get_register_service")
    def test_register_user_success(self, mock_get_service):
        # Given
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_user = User(Email("test@spookymotion.com"), "hashed_password", False, None)
        mock_service.register_user.return_value = mock_user
        request = RegisterUserRequest(
            email="test@spookymotion.com", password="password123"
        )

        # When
        response = register_user(request, mock_service)

        # Then
        assert response.email == "test@spookymotion.com"
        mock_service.register_user.assert_called_once_with(
            "test@spookymotion.com", "password123"
        )

    @patch("src.infrastructure.dependencies.get_register_service")
    def test_register_user_failure(self, mock_get_service):
        # Given
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.register_user.side_effect = ValueError("Invalid email")
        request = RegisterUserRequest(email="invalid", password="short")

        # When/Then
        with pytest.raises(HTTPException) as exception:
            register_user(request, mock_service)
        assert exception.value.status_code == status.HTTP_400_BAD_REQUEST

    @patch("src.infrastructure.dependencies.get_activate_service")
    @patch("src.infrastructure.dependencies.verify_credentials")
    def test_activate_user_success(self, mock_verify_credentials, mock_get_service):
        # Given
        mock_service = MagicMock(spec=ActivateUserService)
        mock_get_service.return_value = mock_service
        mock_verify_credentials.return_value = "test@spookymotion.com"
        mock_user = User(Email("test@spookymotion.com"), "hashed_password", True, None)
        mock_service.activate_user.return_value = mock_user
        request = ActivateUserRequest(activation_code="1234")

        # When
        result = activate_user(request, mock_service, "test@spookymotion.com")

        # Then
        assert result.email == "test@spookymotion.com"
        assert result.is_active == True
        mock_service.activate_user.assert_called_once_with(
            "test@spookymotion.com", "1234"
        )

    @patch("src.infrastructure.dependencies.get_activate_service")
    @patch("src.infrastructure.dependencies.verify_credentials")
    def test_activate_user_service_error(
        self, mock_verify_credentials, mock_get_service
    ):
        # Given
        mock_service = MagicMock(spec=ActivateUserService)
        mock_get_service.return_value = mock_service
        mock_verify_credentials.return_value = "test@spookymotion.com"
        mock_service.activate_user.side_effect = ValueError("Invalid activation code")
        request = ActivateUserRequest(activation_code="000000")

        # When/Then
        with pytest.raises(HTTPException) as exception:
            activate_user(request, mock_service, "test@spookymotion.com")
        assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
        assert str(exception.value.detail) == "Invalid activation code"

    @patch("src.infrastructure.dependencies.get_activate_service")
    @patch("src.infrastructure.dependencies.verify_credentials")
    def test_activate_user_unexpected_error(
        self, mock_verify_credentials, mock_get_service
    ):
        # Given
        mock_service = MagicMock(spec=ActivateUserService)
        mock_get_service.return_value = mock_service
        mock_verify_credentials.return_value = "test@spookymotion.com"
        mock_service.activate_user.side_effect = Exception("Unexpected error")
        request = ActivateUserRequest(activation_code="123456")

        # When/Then
        with pytest.raises(HTTPException) as exception:
            activate_user(request, mock_service, "test@spookymotion.com")
        assert exception.value.status_code == status.HTTP_400_BAD_REQUEST
        assert str(exception.value.detail) == "Unexpected error"
