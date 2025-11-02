from datetime import datetime, timedelta, timezone

import pytest
import uuid

from src.domain.exception import (
    ExpiredActivationCodeException,
    InvalidActivationCodeException,
    UserAlreadyActiveException,
)
from src.domain.model import Email, User, ActivationCode


def test_user_creation():
    email = Email("test@spookymotion.com")
    user = User(id=uuid.uuid4(), email=email, password_hash="hashed_password")
    assert user.id is not None
    assert user.email == email
    assert not user.is_active
    assert user.activation_code is None


def test_user_activation_success():
    email = Email("test@spookymotion.com")
    activation_code = ActivationCode(
        value="1234", expires_at=ActivationCode.compute_expiration_datetime()
    )
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash="hashed_password",
        activation_code=activation_code,
    )

    user.activate("1234")
    assert user.is_active
    assert user.activation_code is None


def test_user_activation_fails_with_wrong_code():
    email = Email("test@spookymotion.com")
    activation_code = ActivationCode(
        value="1234", expires_at=ActivationCode.compute_expiration_datetime()
    )
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash="hashed_password",
        activation_code=activation_code,
    )

    with pytest.raises(InvalidActivationCodeException) as e:
        user.activate("0000")
    assert "Invalid activation code" in str(e.value)


def test_user_activation_fails_with_expired_code():
    email = Email("test@spookymotion.com")
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    activation_code = ActivationCode(value="1234", expires_at=past)
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash="hashed_password",
        activation_code=activation_code,
    )

    with pytest.raises(ExpiredActivationCodeException) as e:
        user.activate("1234")
    assert "expired" in str(e.value)


def test_user_activation_fails_if_already_active():
    email = Email("test@spookymotion.com")
    user = User(
        id=uuid.uuid4(), email=email, password_hash="hashed_password", is_active=True
    )

    with pytest.raises(UserAlreadyActiveException) as e:
        user.activate("1234")
    assert "already active" in str(e.value)
