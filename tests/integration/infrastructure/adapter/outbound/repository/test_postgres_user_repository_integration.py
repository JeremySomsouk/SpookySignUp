from datetime import timedelta

from src.domain.model import User, Email, ActivationCode
from src.infrastructure.adapter.outbound.repository import PostgresUserRepository


class TestPostgresUserRepository:
    """Integration tests for PostgresUserRepository"""

    def test_save_and_find_user(self, initialized_db):
        """Should save a user and then find them by email"""
        # Given
        repository = PostgresUserRepository(initialized_db)
        test_user = User(
            email=Email("test@spookymotion.com"),
            password_hash="hashed_password",
            is_active=False,
            activation_code=ActivationCode(value="1234", expires_at=ActivationCode.compute_expiration_datetime())
        )

        # When
        repository.save(test_user)
        found_user = repository.find_by_email(test_user.email)

        # Then
        assert found_user is not None
        assert found_user.email.value == test_user.email.value
        assert found_user.password_hash == test_user.password_hash
        assert found_user.is_active == test_user.is_active
        assert found_user.activation_code.value == test_user.activation_code.value

    def test_update_user_fields(self, initialized_db):
        """Should update all fields when saving an existing user"""
        # Given
        repository = PostgresUserRepository(initialized_db)
        original_expiration = ActivationCode.compute_expiration_datetime()
        original_user = User(
            email=Email("update@spookymotion.com"),
            password_hash="original_password",
            is_active=False,
            activation_code=ActivationCode(value="1111", expires_at=original_expiration)
        )

        repository.save(original_user)

        updated_expiration = ActivationCode.compute_expiration_datetime() + timedelta(days=1)
        updated_user = User(
            email=Email("update@spookymotion.com"),  # Same email
            password_hash="updated_password",
            is_active=True,
            activation_code=ActivationCode(value="2222", expires_at=updated_expiration)
        )

        # When
        repository.save(updated_user)
        found_user = repository.find_by_email(original_user.email)

        # Then
        assert found_user is not None
        assert found_user.email.value == updated_user.email.value
        assert found_user.password_hash == updated_user.password_hash
        assert found_user.is_active == updated_user.is_active
        assert found_user.activation_code.value == updated_user.activation_code.value
        assert found_user.activation_code.expires_at == updated_expiration

    def test_find_nonexistent_user(self, initialized_db):
        """Should return None when user doesn't exist"""
        # Given
        repository = PostgresUserRepository(initialized_db)

        # When
        result = repository.find_by_email(Email("nonexistent@spookymotion.com"))

        # Then
        assert result is None
