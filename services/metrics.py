import os
import logging
from typing import Dict

import boto3
from botocore.exceptions import ClientError


_LOGGER = logging.getLogger("metrics")

_REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
_NAMESPACE = os.getenv("CLOUDWATCH_METRICS_NAMESPACE", "NotificationService")

_CLOUDWATCH = boto3.client("cloudwatch", region_name=_REGION)


def publish_notification_metric(dimensions: Dict[str, str]) -> None:
    """
    Publish a single CloudWatch metric data point when a notification is sent.

    Failures are logged but do not break the main request flow.
    """
    try:
        _CLOUDWATCH.put_metric_data(
            Namespace=_NAMESPACE,
            MetricData=[
                {
                    "MetricName": "NotificationsPublished",
                    "Dimensions": [
                        {"Name": name, "Value": value} for name, value in dimensions.items()
                    ],
                    "Unit": "Count",
                    "Value": 1.0,
                }
            ],
        )
    except ClientError as exc:
        _LOGGER.warning("Failed to publish CloudWatch metric: %s", exc)

