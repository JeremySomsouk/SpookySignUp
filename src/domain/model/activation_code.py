import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class ActivationCode:
    """Immutable value object representing a 4-digit activation code"""

    value: str
    expires_at: datetime

    @classmethod
    def generate_activation_code(cls) -> "ActivationCode":
        return cls(
            value=cls.generate_code(),
            expires_at=cls.compute_expiration_datetime(),
        )

    def has_code_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    @staticmethod
    def generate_code() -> str:
        """Generate an activation code between 0000 and 9999."""
        return f"{secrets.randbelow(10000):04d}"

    @staticmethod
    def compute_expiration_datetime() -> datetime:
        return datetime.now(timezone.utc) + timedelta(minutes=1)
