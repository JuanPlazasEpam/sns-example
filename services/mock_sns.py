# services/mock_sns.py
from services.mock_sqs import send_message

class MockSNSService:
    """Simulate SNS publishing to SQS"""
    def publish(self, subject: str, message: str):
        payload = {
            "Subject": subject,
            "Message": message
        }
        send_message(payload)  # SNS → SQS
        return {"MessageId": "mock-sns-id"}
