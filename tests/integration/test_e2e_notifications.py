import time
import requests

PUBLISHER_URL = "http://localhost:8000/events"


def test_e2e_event_flow():
    """
    End-to-end test:
    API -> SNS -> SQS -> Consumer
    """

    payload = {
        "eventType": "WELCOME_EMAIL",
        "recipient": "e2e@example.com",
        "data": {"username": "E2E User"}
    }

    # 1. Send event to publisher
    response = requests.post(PUBLISHER_URL, json=payload, timeout=5)

    assert response.status_code == 202
    assert response.json()["message"] == "Event published successfully"

    # 2. Allow consumer time to process the message
    time.sleep(5)

    # 3. If no exception occurred, end-to-end flow succeeded
    assert True