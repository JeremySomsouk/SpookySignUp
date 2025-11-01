from dataclasses import dataclass

from src.domain.model import User


@dataclass(frozen=True)
class UserResponse:
    email: str
    is_active: bool

    @staticmethod
    def from_domain(user: User) -> "UserResponse":
        return UserResponse(
            email=user.email.value,
            is_active=user.is_active,
        )
