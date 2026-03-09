import os
import json
import time
from typing import Dict, Optional

import boto3
from botocore.exceptions import ClientError


_REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL") or os.getenv("SQS_QUEUE_URL")
_MAX_RECEIVE_RETRIES = int(os.getenv("SQS_RECEIVE_MAX_RETRIES", "3"))

if not _QUEUE_URL:
    raise RuntimeError("AWS_SQS_QUEUE_URL or SQS_QUEUE_URL environment variable must be set for AWS backend.")

_SQS_CLIENT = boto3.client("sqs", region_name=_REGION)


def _normalize_sns_sqs_body(raw_body: str) -> Dict[str, str]:
    """
    Convert the SNS-over-SQS body into the same shape used by the mock queue:
    {
        "Subject": "...",
        "Message": "..."
    }
    """
    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        # If the body is not JSON, treat it as a plain message string.
        return {"Subject": "Notification", "Message": raw_body}

    subject = data.get("Subject") or data.get("subject") or "Notification"
    message = data.get("Message") or data.get("message") or raw_body
    return {"Subject": subject, "Message": message}


def _receive_with_retry() -> Optional[Dict]:
    """
    Wrap SQS receive_message with a simple retry strategy for transient errors.
    """
    attempt = 0
    while True:
        try:
            return _SQS_CLIENT.receive_message(
                QueueUrl=_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=1,
            )
        except ClientError as exc:
            # Retry on transient AWS or network errors.
            attempt += 1
            if attempt >= _MAX_RECEIVE_RETRIES:
                raise
            sleep_seconds = 2**attempt
            time.sleep(sleep_seconds)


def receive_message() -> Optional[Dict]:
    """
    Receive a single message from the real SQS queue and normalize it to:
    {
        "MessageId": "...",
        "Body": {
            "Subject": "...",
            "Message": "..."
        }
    }
    """
    try:
        resp = _receive_with_retry()
    except _SQS_CLIENT.exceptions.QueueDoesNotExist:
        raise RuntimeError(f"SQS queue at URL '{_QUEUE_URL}' does not exist.")

    messages = resp.get("Messages")
    if not messages:
        return None

    msg = messages[0]
    receipt_handle = msg["ReceiptHandle"]
    raw_body = msg.get("Body", "")

    # Delete message immediately so it doesn't get reprocessed.
    _SQS_CLIENT.delete_message(QueueUrl=_QUEUE_URL, ReceiptHandle=receipt_handle)

    normalized_body = _normalize_sns_sqs_body(raw_body)

    return {
        "MessageId": msg.get("MessageId"),
        "Body": normalized_body,
    }

