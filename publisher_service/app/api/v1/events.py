from fastapi import APIRouter, HTTPException, status
from app.schemas import EventPayload
import boto3
import os
import uuid
import json

router = APIRouter()

sns = boto3.client(
    "sns",
    region_name=os.getenv("AWS_REGION"),
    endpoint_url=os.getenv("AWS_ENDPOINT_URL")  # REQUIRED for LocalStack
)

TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def publish_event(payload: EventPayload):
    try:
        event_id = str(uuid.uuid4())

        message = payload.model_dump()
        message["eventId"] = event_id

        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(message),
            MessageAttributes={
                "eventType": {
                    "DataType": "String",
                    "StringValue": payload.eventType
                },
                "recipient": {
                    "DataType": "String",
                    "StringValue": payload.recipient
                }
            }
        )

        return {
            "message": "Event published successfully",
            "eventId": event_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
