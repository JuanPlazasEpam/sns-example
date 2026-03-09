import os
from importlib import reload


def test_aws_sns_publish_fifo_adds_group_and_dedup(monkeypatch):
    os.environ["AWS_REGION"] = "us-east-2"
    os.environ["AWS_SNS_TOPIC_ARN"] = "arn:aws:sns:us-east-2:123456789012:example.fifo"

    # Capture the arguments passed to boto3 SNS client.publish.
    calls = []

    class DummySNSClient:
        def publish(self, **kwargs):
            calls.append(kwargs)
            return {"MessageId": "123"}

    def fake_boto3_client(service_name, region_name=None):
        assert service_name == "sns"
        return DummySNSClient()

    import services.aws_sns as aws_sns_module

    monkeypatch.setattr(aws_sns_module, "boto3", type("Boto3Stub", (), {"client": staticmethod(fake_boto3_client)}))
    aws_sns = reload(aws_sns_module)

    svc = aws_sns.AwsSNSService()
    result = svc.publish(subject="Test", message="Payload")

    assert result["MessageId"] == "123"
    assert len(calls) == 1
    kwargs = calls[0]
    assert kwargs["TopicArn"].endswith(".fifo")
    assert kwargs["Subject"] == "Test"
    assert kwargs["Message"] == "Payload"
    assert kwargs["MessageGroupId"] == "default"
    # Deduplication ID should be present for FIFO topics.
    assert "MessageDeduplicationId" in kwargs and kwargs["MessageDeduplicationId"]

