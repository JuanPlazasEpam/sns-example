# desktop_app.py
import sys
import time
import requests

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget
from PyQt6.QtCore import Qt, QThread, pyqtSignal

API_URL = "http://127.0.0.1:8000/mock-sqs/receive"

class PollWorker(QThread):
    notification_received = pyqtSignal(str, str)

    def run(self):
        while True:
            try:
                response = requests.get(API_URL, timeout=5).json()
                message = response.get("message")
                if message:
                    self.notification_received.emit(message["Subject"], message["Message"])
            except Exception as e:
                print("Polling error:", e)
            time.sleep(1)  # simulate SQS long polling

class NotificationApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("📬 Mock Notifications")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        title = QLabel("Mock SQS Messages")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.list_widget = QListWidget()

        layout.addWidget(title)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

        self.worker = PollWorker()
        self.worker.notification_received.connect(self.add_notification)
        self.worker.start()

    def add_notification(self, subject: str, message: str):
        self.list_widget.addItem(f"{subject}: {message}")

def main():
    app = QApplication(sys.argv)
    window = NotificationApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
