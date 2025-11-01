import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Immutable value object representing a user email"""

    value: str

    def __post_init__(self):
        """Validates the email format on initialization."""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise ValueError(f"Invalid email format: {self.value}")
        if len(self.value) > 254:
            raise ValueError(f"Email too long: {self.value}")
