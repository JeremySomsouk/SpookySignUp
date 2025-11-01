from dataclasses import dataclass
from typing import Optional

from domain.exception import (
    UserAlreadyActiveException,
    ExpiredActivationCodeException,
    InvalidActivationCodeException,
)
from .activation_code import ActivationCode
from .email import Email


@dataclass
class User:
    """Domain entity representing a user account"""

    email: Email
    password_hash: str
    is_active: bool = False
    activation_code: Optional[ActivationCode] = None

    def activate(self, provided_code: str) -> None:
        """Activates the user if the provided code matches and is not expired"""
        if self.is_active:
            raise UserAlreadyActiveException(f"User ({self.email}) already active.")
        if self.activation_code is None:
            raise ValueError("No activation code set")
        if self.activation_code.value != provided_code:
            raise InvalidActivationCodeException("Invalid activation code.")
        if self.activation_code.has_code_expired():
            raise ExpiredActivationCodeException("Activation code has expired.")
        self.is_active = True
        self.activation_code = None
