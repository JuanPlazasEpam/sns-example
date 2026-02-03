from pydantic import BaseModel

class NotificationRequest(BaseModel):
    subject: str
    message: str