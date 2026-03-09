from services.aws_sqs import _normalize_sns_sqs_body


def test_normalize_sns_sqs_body_from_sns_payload():
    raw = '{"Type":"Notification","Subject":"Hello","Message":"World"}'
    result = _normalize_sns_sqs_body(raw)
    assert result == {"Subject": "Hello", "Message": "World"}


def test_normalize_sns_sqs_body_plain_text():
    raw = "just a plain message"
    result = _normalize_sns_sqs_body(raw)
    assert result == {"Subject": "Notification", "Message": raw}

