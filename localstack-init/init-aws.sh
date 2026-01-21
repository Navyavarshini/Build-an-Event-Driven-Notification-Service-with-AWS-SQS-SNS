#!/bin/bash
set -e

# Required for awslocal
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

QUEUE_NAME="notification-queue"
TOPIC_NAME="notification-events"

QUEUE_URL="http://localhost:4566/000000000000/${QUEUE_NAME}"
QUEUE_ARN="arn:aws:sqs:us-east-1:000000000000:${QUEUE_NAME}"
TOPIC_ARN="arn:aws:sns:us-east-1:000000000000:${TOPIC_NAME}"

echo "Creating SNS topic..."
awslocal sns create-topic --name "$TOPIC_NAME"

echo "Creating SQS queue..."
awslocal sqs create-queue --queue-name "$QUEUE_NAME"

echo "Waiting for SQS queue to become available..."
until awslocal sqs get-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attribute-names QueueArn >/dev/null 2>&1; do
  sleep 1
done

echo "Subscribing SQS queue to SNS topic..."
awslocal sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol sqs \
  --notification-endpoint "$QUEUE_ARN" \
  --attributes RawMessageDelivery=true

echo "Setting SQS access policy for SNS..."
awslocal sqs set-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attributes Policy="file:///etc/localstack/init/ready.d/sqs-policy.json"

echo "✅ LocalStack AWS resources created successfully"