import boto3
import os
import time
import json
from botocore.exceptions import ClientError, EndpointConnectionError

AWS_REGION = os.getenv("AWS_REGION")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
QUEUE_URL = os.getenv("SQS_QUEUE_URL")

sqs = boto3.client(
    "sqs",
    region_name=AWS_REGION,
    endpoint_url=AWS_ENDPOINT_URL
)


def wait_for_localstack():
    """Wait until LocalStack endpoint is reachable"""
    print("Waiting for LocalStack to be ready...")
    while True:
        try:
            sqs.list_queues()
            print("LocalStack is reachable.")
            break
        except EndpointConnectionError:
            time.sleep(2)


def wait_for_queue():
    """Wait until the SQS queue exists"""
    print("Waiting for SQS queue to be available...")
    while True:
        try:
            sqs.get_queue_attributes(
                QueueUrl=QUEUE_URL,
                AttributeNames=["QueueArn"]
            )
            print("SQS queue is available. Starting consumer...")
            break
        except ClientError as e:
            if e.response["Error"]["Code"] == "AWS.SimpleQueueService.NonExistentQueue":
                time.sleep(2)
            else:
                raise


def process_message(body: str):
    """
    Supports both:
    1. Raw SNS delivery (RawMessageDelivery=true)
    2. Standard SNS envelope
    """
    payload = json.loads(body)

    # If SNS envelope exists, unwrap it
    if "Message" in payload:
        event = json.loads(payload["Message"])
    else:
        event = payload  # Raw message delivery
    
    print(
    f"Processing event '{event.get('eventType')}' "
    f"for '{event.get('recipient')}' "
    f"with data: {event.get('data')}",
    flush=True
)


def poll():
    wait_for_localstack()
    wait_for_queue()

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20
            )

            messages = response.get("Messages", [])

            for message in messages:
                try:
                    process_message(message["Body"])

                    sqs.delete_message(
                        QueueUrl=QUEUE_URL,
                        ReceiptHandle=message["ReceiptHandle"]
                    )
                    print("Deleted message:", message["MessageId"])

                except Exception as e:
                    print(
                        f"Error processing message {message.get('MessageId')}: {e}. "
                        "Message will not be deleted."
                    )

        except Exception as e:
            print(f"Error polling SQS: {e}")

        time.sleep(1)

if __name__ == "__main__":
    poll()