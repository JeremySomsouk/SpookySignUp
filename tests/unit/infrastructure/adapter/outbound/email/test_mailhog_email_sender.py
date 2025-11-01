import smtplib
from unittest.mock import MagicMock, patch

import pytest

from src.domain.model import Email
from src.domain.port import EmailDeliveryException
from src.infrastructure.adapter.outbound import MailhogEmailSender
from src.infrastructure.config import SmtpConfig


@pytest.fixture
def smtp_config():
    return SmtpConfig(
        host="localhost",
        port=1025,
        timeout=10,
        sender_email="noreply@spookymotion.com",
    )


@pytest.fixture
def email_sender(smtp_config):
    return MailhogEmailSender(smtp_config)


def test_send_activation_email_success(email_sender):
    mock_smtp = MagicMock()
    mock_smtp.__enter__.return_value = mock_smtp

    with patch("smtplib.SMTP", return_value=mock_smtp):
        email_sender.send_activation_email(Email("test@spookymotion.com"), "1234")

    mock_smtp.send_message.assert_called_once()
    message = mock_smtp.send_message.call_args[0][0]
    assert message["Subject"] == "Activate Your Account"
    assert message["From"] == "noreply@spookymotion.com"
    assert message["To"] == "test@spookymotion.com"
    assert "Your activation code is: 1234" in str(message.get_payload())


def test_send_activation_email_failure(email_sender):
    mock_smtp = MagicMock()
    mock_smtp.__enter__.return_value = mock_smtp
    mock_smtp.send_message.side_effect = smtplib.SMTPException("Connection failed")

    with patch("smtplib.SMTP", return_value=mock_smtp):
        with pytest.raises(EmailDeliveryException) as exception:
            email_sender.send_activation_email(Email("test@spookymotion.com"), "1234")

    assert str(exception.value) == "SMTP error: Connection failed"
