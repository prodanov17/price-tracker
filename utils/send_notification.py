import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_URL = os.getenv("PUSHOVER_API_URL")
TIMESTAMP_FILE = './utils/tmp/notification_timestamp.txt'
THRESHOLD = 3600  # 6 hours in seconds

def get_last_notified_time():
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, 'r') as f:
            try:
                return float(f.read().strip())
            except ValueError:
                return 0
    return 0

def update_last_notified_time():
    with open(TIMESTAMP_FILE, 'w') as f:
        f.write(str(time.time()))

def notify(message, force=False):
    current_time = time.time()
    last_notified_time = get_last_notified_time()

    if current_time - last_notified_time > THRESHOLD or force:
        data = {
            "message": message,
            "user": os.getenv('PUSHOVER_USER_KEY'),
            "token": os.getenv('PUSHOVER_API_KEY'),
        }

        response = requests.post(API_URL, json=data)

        if response.status_code == 200:
            print("Notification sent successfully.")
            update_last_notified_time()
        else:
            print(f"Failed to send notification. Status code: {response.status_code}")
    else:
        print("Notification suppressed to prevent spamming.")
