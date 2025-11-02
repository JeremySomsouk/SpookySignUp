import uuid
from dataclasses import dataclass

from src.domain.model import User


@dataclass(frozen=True)
class UserResponse:
    id: uuid.UUID
    email: str
    is_active: bool

    @staticmethod
    def from_domain(user: User) -> "UserResponse":
        return UserResponse(
            id=user.id,
            email=user.email.value,
            is_active=user.is_active,
        )
