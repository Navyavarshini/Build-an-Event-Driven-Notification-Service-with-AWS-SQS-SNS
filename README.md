Event-Driven Notification Service

This project implements a robust, scalable Notification Service using an Event-Driven Architecture (EDA) pattern with AWS SNS and SQS.

The system is designed as two fully decoupled microservices:

A Publisher Service that exposes an HTTP API to accept notification events and publishes them to an SNS topic.

A Consumer Service that asynchronously consumes events from an SQS queue subscribed to the SNS topic and processes them independently.

The architecture ensures loose coupling, high scalability, fault tolerance, and reliable message delivery.
This approach allows the publisher to remain responsive while notification processing happens asynchronously, making the system suitable for modern cloud-native, distributed environments.

Setup Instructions
Prerequisites
Ensure the following tools are installed on your system:
    Docker
    Docker Compose
    Python 3.9+ (required only for running end-to-end tests from host)
    Git

AWS / LocalStack Configuration

This project uses AWS SNS and SQS.
For local development and testing, AWS services are simulated using LocalStack.

No real AWS account is required for local execution.

Environment Variables

Create a .env file in the project root using the provided .env.example file as reference.

Example:

    AWS_ACCESS_KEY_ID=test
    AWS_SECRET_ACCESS_KEY=test
    AWS_REGION=us-east-1

    SNS_TOPIC_ARN=arn:aws:sns:us-east-1:000000000000:notification-events
    SQS_QUEUE_URL=http://localhost:4566/000000000000/notification-queue
    AWS_ENDPOINT_URL=http://localhost:4566

Install Python Dependencies (for E2E testing only)
From the project root:
        python -m pip install pytest requests boto3

Docker containers handle all runtime dependencies automatically.

How to Run the Application
1. Start all services
   From the project root directory, run:
        docker-compose up --build


This command will:
    Build the publisher and consumer Docker images
    Start LocalStack, publisher, and consumer services
    Automatically wire SNS → SQS → Consumer

2. Verify publisher service is running
Open a new terminal and run:
    curl http://localhost:8000/health

Expected response:
    {"status":"ok"}

3. Publish a test event
        curl -X POST http://localhost:8000/events \
        -H "Content-Type: application/json" \
        -d '{
            "eventType": "WELCOME_EMAIL",
            "recipient": "test@example.com",
            "data": { "username": "John Doe" }
        }'


Expected response (HTTP 202 Accepted):
        {
        "message": "Event published successfully",
        "eventId": "<uuid>"
        }

4. Verify consumer processing
     Check consumer logs:
       docker-compose logs consumer


You should see output similar to:
            Processing event 'WELCOME_EMAIL' for 'test@example.com' with data: {'username': 'John Doe'}


This confirms:
   Event was published to SNS
   Delivered to SQS
   Consumed and deleted successfully

Stopping the application
    To stop and clean up containers:
            docker-compose down -v

How to Run Tests
1. Run publisher unit tests
    docker-compose exec publisher pytest -vv


This runs:
    Input validation tests
    SNS publishing logic tests
    Error handling tests

Expected result:
    2 passed

2. Run consumer unit tests
      docker-compose exec consumer pytest -vv


This verifies:
    Message processing logic
    Successful message deletion
    Failure handling (message not deleted on error)

Expected result:
    3 passed

3. Run End-to-End (E2E) integration test

⚠️ This test must be run from the host machine, not inside a container.

Ensure services are running:
       docker-compose up -d


Then execute:
    python -m pytest tests/integration/test_e2e_notifications.py -vv


Expected result:
    test_e2e_event_flow PASSED

This confirms the complete flow:
    API → SNS → SQS → Consumer → Message Deletion

4. Notes on warnings
You may see warnings similar to:

PythonDeprecationWarning: Boto3 will no longer support Python 3.9

These warnings do not affect functionality and are expected when using Python 3.9 with newer AWS SDK versions.


API Documentation
POST /events
Publishes a notification event to the system using an event-driven architecture.

Endpoint
  POST /events


Request Headers
    Content-Type: application/json


Request Body
    {
    "eventType": "string",
    "recipient": "string",
    "data": {}
    }

Field	Type	Required	Description
eventType	string	Yes	Identifier for the event type (e.g., WELCOME_EMAIL)
recipient	string	Yes	Notification recipient (e.g., email address)
data	object	Yes	Event-specific payload
Success Response

HTTP 202 Accepted
        {
        "message": "Event published successfully",
        "eventId": "uuid"
        }


The event is accepted for processing.
Delivery is handled asynchronously via SNS and SQS.

Error Response
HTTP 400 Bad Request
        {
        "error": "Invalid request payload",
        "details": [
            "'eventType' field is required"
        ]
        }


Returned when:
    Required fields are missing
    Payload structure is invalid

Example curl request
        curl -X POST http://localhost:8000/events \
            -H "Content-Type: application/json" \
            -d '{
                "eventType": "WELCOME_EMAIL",
                "recipient": "test@example.com",
                "data": { "username": "John Doe" }
            }'


Architectural Decisions
Event-Driven Architecture (EDA)
    This project follows an Event-Driven Architecture to decouple the notification request producer from the notification processing logic.
    The publisher service is responsible only for accepting and validating incoming requests, while the consumer service handles processing asynchronously.

This approach improves:
    Scalability
    Fault isolation
    Independent service deployment

AWS SNS + SQS
      SNS (Simple Notification Service) is used for event publishing
      SQS (Simple Queue Service) is subscribed to the SNS topic to ensure reliable message delivery

This combination provides:
        Message durability
        Automatic retries
        Loose coupling between services

The publisher does not wait for the consumer to process messages, ensuring non-blocking behavior.

Consumer Reliability

The consumer service:
        Continuously polls the SQS queue
        Processes messages one at a time
        Deletes messages only after successful processing

If processing fails, the message is not deleted and becomes visible again, allowing retries.


Containerized Microservices

Both services are:
    Independently containerized using Docker
    Built using multi-stage Dockerfiles for smaller images
    Orchestrated locally using Docker Compose

This mirrors real-world cloud-native deployment patterns.

Configuration & Security
        All AWS credentials and service configuration values are provided via environment variables
        No sensitive data is hardcoded
        Supports LocalStack for local development and testing

Potential Improvements / Future Work

Dead Letter Queue (DLQ)
   Introduce an SQS Dead Letter Queue to capture messages that fail processing multiple times.

Message Idempotency
   Track processed message IDs to prevent duplicate processing.

Structured Logging & Metrics
   Integrate structured logging and basic metrics for better observability.

Horizontal Scaling
   Deploy multiple consumer instances to process messages in parallel.

Authentication & Rate Limiting 
   Add authentication and rate limiting to the publisher API.