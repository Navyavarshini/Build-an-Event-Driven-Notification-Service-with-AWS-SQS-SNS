import os
import json
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
import boto3

from app.main import app


@pytest.fixture(scope="function")
def client():
    """
    Creates a FastAPI test client with mocked SNS
    """
    with mock_aws():
        # Environment variables required by the app
        os.environ["AWS_ACCESS_KEY_ID"] = "test"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
        os.environ["AWS_REGION"] = "us-east-1"
        # os.environ["AWS_ENDPOINT_URL"] = "http://localhost:4566"

        # Create mocked SNS topic
        sns = boto3.client("sns", region_name="us-east-1")
        topic = sns.create_topic(Name="notification-events")
        os.environ["SNS_TOPIC_ARN"] = topic["TopicArn"]

        yield TestClient(app)


def test_publish_event_success(client):
    payload = {
        "eventType": "WELCOME_EMAIL",
        "recipient": "test@example.com",
        "data": {
            "username": "John Doe"
        }
    }

    response = client.post("/events", json=payload)

    assert response.status_code == 202

    body = response.json()
    assert body["message"] == "Event published successfully"
    assert "eventId" in body
    assert isinstance(body["eventId"], str)


def test_publish_event_invalid_payload(client):
    # Missing eventType
    payload = {
        "recipient": "test@example.com",
        "data": {}
    }

    response = client.post("/events", json=payload)

    # FastAPI validation error
    assert response.status_code == 400
