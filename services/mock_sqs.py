# services/mock_sqs.py
from queue import Queue
from typing import Dict
import uuid

# Global in-memory queue acting like SQS
_mock_queue = Queue()


def send_message(message: Dict):
    """Simulate sending a message to SQS"""
    _mock_queue.put({
        "MessageId": str(uuid.uuid4()),
        "Body": message
    })


def receive_message():
    """Simulate receiving a message from SQS"""
    if _mock_queue.empty():
        return None
    return _mock_queue.get()
