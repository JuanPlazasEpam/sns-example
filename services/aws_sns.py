import os
import uuid

import boto3


class AwsSNSService:
    """Real SNS publisher using boto3."""

    def __init__(self) -> None:
        # Support both AWS_REGION and AWS_DEFAULT_REGION
        self.region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        # Support both AWS_SNS_TOPIC_ARN and SNS_TOPIC_ARN (from .env)
        self.topic_arn = os.getenv("AWS_SNS_TOPIC_ARN") or os.getenv("SNS_TOPIC_ARN")

        if not self.topic_arn:
            raise RuntimeError("AWS_SNS_TOPIC_ARN or SNS_TOPIC_ARN environment variable must be set for AWS backend.")

        self.client = boto3.client("sns", region_name=self.region)

    def publish(self, subject: str, message: str):
        """Publish a notification to a real SNS topic."""
        kwargs = {
            "TopicArn": self.topic_arn,
            "Subject": subject,
            "Message": message,
        }

        # If this is a FIFO topic, we must include a MessageGroupId (and often a deduplication ID).
        if self.topic_arn.endswith(".fifo"):
            kwargs["MessageGroupId"] = "default"
            # Use a random deduplication ID so each message is treated as unique.
            kwargs["MessageDeduplicationId"] = str(uuid.uuid4())

        response = self.client.publish(**kwargs)

        # Normalize return shape to match the mock service.
        return {"MessageId": response.get("MessageId")}

