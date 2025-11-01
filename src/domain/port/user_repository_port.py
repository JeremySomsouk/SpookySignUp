from abc import ABC, abstractmethod
from typing import Optional

from src.domain.model import Email, User


class UserRepositoryPort(ABC):
    """Interface (port) for user persistence operations"""

    @abstractmethod
    def save(self, user: User) -> None:
        """Saves a user or update the code of a user to the repository"""
        pass

    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[User]:
        """Finds a user by email"""
        pass
