import pytest

from src.domain.model import Email


def test_email_validation():
    # Valid email
    Email("test@example.com")

    # Invalid email format
    with pytest.raises(ValueError) as e:
        Email("invalid")
    assert "Invalid email format" in str(e.value)

    # Email too long
    with pytest.raises(ValueError) as e:
        Email("a" * 300 + "@example.com")
    assert "Email too long" in str(e.value)
