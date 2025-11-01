from dataclasses import dataclass


@dataclass
class SmtpConfig:
    """Configuration for the SMTP email sender"""

    host: str = "smtp"
    port: int = 1025
    timeout: int = 10
    sender_email: str = "noreply@spookymotion.com"
