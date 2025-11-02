import time

import requests

from src.domain.model import Email


class TestMailhogIntegration:
    """Integration tests for MailHog email sending"""

    def test_send_activation_email(self, email_sender, mailhog_container):
        # Given
        test_email = Email("user@spookymotion.com")
        activation_code = "9192"
        requests.delete("http://localhost:8025/api/v1/messages")

        # When
        email_sender.send_activation_email(test_email, activation_code)

        # Then
        time.sleep(1)
        response = requests.get("http://localhost:8025/api/v2/messages")
        assert response.status_code == 200

        emails = response.json()
        assert len(emails["items"]) == 1

        email_data = emails["items"][0]
        assert email_data["To"][0]["Mailbox"] == "user"
        assert email_data["To"][0]["Domain"] == "spookymotion.com"
        assert email_data["From"]["Mailbox"] == "noreply"
        assert email_data["From"]["Domain"] == "spookymotion.com"
        assert email_data["Content"]["Headers"]["Subject"][0] == "Activate Your Account"
        assert "Your activation code is: 9192" in email_data["Content"]["Body"]
