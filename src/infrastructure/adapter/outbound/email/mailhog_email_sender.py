import smtplib
from email.mime.text import MIMEText

from src.domain.model import Email
from src.domain.port import EmailSenderPort, EmailDeliveryException
from src.infrastructure.config import SmtpConfig


class MailhogEmailSender(EmailSenderPort):
    def __init__(self, config: SmtpConfig = SmtpConfig()):
        self.config = config

    def send_activation_email(self, email: Email, activation_code: str) -> None:
        message = MIMEText(f"Your activation code is: {activation_code}")
        message["Subject"] = "Activate Your Account"
        message["From"] = self.config.sender_email
        message["To"] = email.value

        try:
            with smtplib.SMTP(
                host=self.config.host,
                port=self.config.port,
                timeout=self.config.timeout,
            ) as server:
                server.send_message(message)
        except smtplib.SMTPException as exception:
            raise EmailDeliveryException(f"SMTP error: {exception}")
