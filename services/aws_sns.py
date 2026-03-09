import os
import time
import uuid

import boto3
from botocore.exceptions import ClientError


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
        self._max_publish_retries = int(os.getenv("SNS_PUBLISH_MAX_RETRIES", "3"))

    def publish(self, subject: str, message: str):
        """Publish a notification to a real SNS topic with basic retry on transient errors."""
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

        attempt = 0
        while True:
            try:
                response = self.client.publish(**kwargs)
                # Normalize return shape to match the mock service.
                return {"MessageId": response.get("MessageId")}
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code", "")
                # Only retry on clearly transient errors.
                if error_code not in {"Throttling", "ThrottlingException", "InternalError"}:
                    raise

                attempt += 1
                if attempt >= self._max_publish_retries:
                    raise

                sleep_seconds = 2**attempt
                time.sleep(sleep_seconds)
