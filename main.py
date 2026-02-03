# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from services.mock_sns import MockSNSService
from services.mock_sqs import receive_message

app = FastAPI(title="Mock Notification API")

sns_service = MockSNSService()

class NotificationRequest(BaseModel):
    subject: str
    message: str

@app.post("/notifications")
def send_notification(payload: NotificationRequest):
    """Receive notification and publish to mock SNS"""
    sns_service.publish(
        subject=payload.subject,
        message=payload.message
    )
    return {"status": "sent", "mock": True}

@app.get("/mock-sqs/receive")
def receive_mock_message():
    """Endpoint to poll the mock SQS"""
    msg = receive_message()
    if not msg:
        return {"message": None}
    return {"message": msg["Body"]}
