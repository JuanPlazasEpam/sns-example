import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent
APP_ENV = os.getenv("APP_ENV", "local").lower()

# Load environment variables from an environment-specific file if present.
# - local: .env
# - test:  .env.test
# - prod:  .env.prod
env_filename = ".env" if APP_ENV == "local" else f".env.{APP_ENV}"
load_dotenv(dotenv_path=BASE_DIR / env_filename)

BACKEND = os.getenv("NOTIFICATIONS_BACKEND", "mock").lower()

app = FastAPI(title=f"Notification API ({APP_ENV})")


if BACKEND == "aws":
    from services.aws_sns import AwsSNSService
    from services.aws_sqs import receive_message as receive_message_impl

    sns_service = AwsSNSService()
    receive_message = receive_message_impl
else:
    from services.mock_sns import MockSNSService
    from services.mock_sqs import receive_message as receive_message_impl

    sns_service = MockSNSService()
    receive_message = receive_message_impl


class NotificationRequest(BaseModel):
    subject: str
    message: str


@app.post("/notifications")
def send_notification(payload: NotificationRequest):
    """Receive notification and publish using the configured backend (mock or AWS)."""
    sns_service.publish(
        subject=payload.subject,
        message=payload.message,
    )
    return {"status": "sent", "backend": BACKEND}


@app.get("/mock-sqs/receive")
def receive_mock_message():
    """Endpoint to poll the configured SQS backend (mock or AWS)."""
    msg = receive_message()
    if not msg:
        return {"message": None}
    return {"message": msg["Body"]}
