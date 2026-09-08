"""
Mock ESP32 script to simulate hardware occupancy events over HTTP.
Useful for bench-testing the backend before actual hardware is flashed.
"""
import requests
import uuid
import time
import datetime
import argparse

API_URL = "http://127.0.0.1:8000/api"
DEVICE_ID = "" # Needs to be populated from DB device
DEVICE_SECRET = "supersecret"

def send_event(event_type: str):
    event_id = str(uuid.uuid4())
    payload = {
        "event_type": event_type,
        "event_id": event_id,
        "occurred_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    headers = {
        "X-Device-Secret": DEVICE_SECRET
    }

    url = f"{API_URL}/devices/{DEVICE_ID}/events"
    try:
        res = requests.post(url, json=payload, headers=headers)
        print(f"Sent {event_type} {event_id} -> {res.status_code} {res.text}")
    except Exception as e:
        print(f"Failed to send {event_type}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device_id", required=True, help="The UUID of the device in DB")
    parser.add_argument("--secret", default="supersecret", help="The device secret")
    parser.add_argument("--action", choices=["ENTRY", "EXIT"], required=True)
    args = parser.parse_args()

    DEVICE_ID = args.device_id
    DEVICE_SECRET = args.secret
    send_event(args.action)
