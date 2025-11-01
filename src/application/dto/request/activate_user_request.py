from dataclasses import dataclass


@dataclass(frozen=True)
class ActivateUserRequest:
    activation_code: str
