from abc import ABC, abstractmethod

from domain.model import Email


class EmailSenderPort(ABC):
    """Interface (port) for sending emails"""

    @abstractmethod
    def send_activation_email(self, email: Email, activation_code: str) -> None:
        pass


class EmailDeliveryException(Exception):
    pass
