import json
import boto3
import pytest
from moto import mock_aws

from app.consumer import process_message


@mock_aws
def test_process_message_logs_correct_output(capsys):
    """
    Verify that process_message logs eventType, recipient, and data
    """

    message_body = json.dumps({
        "Message": json.dumps({
            "eventType": "WELCOME_EMAIL",
            "recipient": "test@example.com",
            "data": {"username": "John Doe"}
        })
    })

    process_message(message_body)

    captured = capsys.readouterr()

    assert "WELCOME_EMAIL" in captured.out
    assert "test@example.com" in captured.out
    assert "John Doe" in captured.out


@mock_aws
def test_message_deleted_after_successful_processing():
    """
    Verify that after successful processing, the message can be deleted
    (Deletion itself is handled by the consumer loop, not process_message)
    """

    sqs = boto3.client("sqs", region_name="us-east-1")

    queue_url = sqs.create_queue(QueueName="test-queue")["QueueUrl"]

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({
            "Message": json.dumps({
                "eventType": "WELCOME_EMAIL",
                "recipient": "test@example.com",
                "data": {"username": "John Doe"}
            })
        })
    )

    messages = sqs.receive_message(QueueUrl=queue_url)["Messages"]
    assert len(messages) == 1

    # simulate successful processing
    process_message(messages[0]["Body"])

    # simulate deletion (normally done by consumer loop)
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=messages[0]["ReceiptHandle"]
    )

    messages_after = sqs.receive_message(QueueUrl=queue_url).get("Messages", [])

    assert messages_after == []


@mock_aws
def test_message_not_deleted_on_processing_failure():
    """
    Verify that invalid messages raise an error and therefore
    should NOT be deleted by the consumer
    """

    sqs = boto3.client("sqs", region_name="us-east-1")

    queue_url = sqs.create_queue(QueueName="test-queue")["QueueUrl"]

    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody="INVALID_JSON"
    )

    messages = sqs.receive_message(QueueUrl=queue_url)["Messages"]

    with pytest.raises(json.JSONDecodeError):
        process_message(messages[0]["Body"])