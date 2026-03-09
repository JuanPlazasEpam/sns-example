import os
from importlib import reload

from fastapi.testclient import TestClient


def _load_app_with_env(backend: str = "mock"):
    os.environ["APP_ENV"] = "local"
    os.environ["NOTIFICATIONS_BACKEND"] = backend

    import main as main_module

    main = reload(main_module)
    return main


def test_send_notification_mock_backend():
    main = _load_app_with_env(backend="mock")

    # Replace the real SNS service with a dummy so we don't depend on implementation details.
    published = []

    class DummySNS:
        def publish(self, subject: str, message: str):
            published.append({"Subject": subject, "Message": message})
            return {"MessageId": "test-id"}

    main.sns_service = DummySNS()

    client = TestClient(main.app)
    resp = client.post(
        "/notifications",
        json={"subject": "Hello", "message": "World"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "sent"
    assert body["backend"] == "mock"

    assert len(published) == 1
    assert published[0] == {"Subject": "Hello", "Message": "World"}

