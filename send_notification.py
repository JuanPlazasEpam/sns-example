import requests

API_URL = "http://127.0.0.1:8000/notifications"  # FastAPI endpoint

def send_notification(subject: str, message: str):
    payload = {
        "subject": subject,
        "message": message
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        response.raise_for_status()  # Raise an error for 4xx/5xx

        data = response.json()
        print(f"Notification sent successfully: {data}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending notification: {e}")


if __name__ == "__main__":
    # Example usage
    send_notification("Build Complete", "Your job finished successfully!")
