import re
import time
import uuid

import pytest
import requests


@pytest.mark.e2e
def test_user_registration_flow():
    """
    End-to-end test for the user registration and activation flow.

    Steps:
    1. Generates a unique email address using a random UUID.
    2. Registers a new user via the registration API endpoint.
    3. Asserts that the registration response returns HTTP 201 (Created).
    4. Retrieves the activation code from the mock email server.
    5. Activates the user account using the activation code.
    6. Asserts that the activation response returns HTTP 200 (OK).
    """
    email = uuid.uuid4().hex + "@spookymotion.com"
    reg_response = requests.post(
        "http://app:8080/api/v1/users/register",
        json={"email": email, "password": "TestPass123!"},
    )
    assert reg_response.status_code == 201

    activation_code = get_activation_code(email)

    activ_response = requests.post(
        "http://app:8080/api/v1/users/activate",
        json={"activation_code": activation_code},
        auth=(email, "TestPass123!"),
    )
    assert activ_response.status_code == 200


def get_activation_code(email):
    max_attempts = 5
    for _ in range(max_attempts):
        time.sleep(1)
        response = requests.get("http://smtp:8025/api/v2/messages?limit=1&to=" + email)
        if response.json()["total"] > 0:
            email_content = response.json()["items"][0]
            # Extract 4-digit activation code from email body
            match = re.search(r"(\d{4})", email_content["Content"]["Body"])
            if match:
                return match.group(0)
    raise Exception("Activation code not found in email")
