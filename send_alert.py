import requests
import json
import uuid
from datetime import datetime

url = 'http://127.0.0.1:5000/add_alert'

data = {
    "uuid": str(uuid.uuid4()),
    "drone_id": "drone123",
    "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
    "alert_type": "Intrusion",
    "description": "Unauthorized person detected in restricted area.",
    "severity": "High",
    "latitude": 37.7749,
    "longitude": -122.4194
}

headers = {
    'Content-Type': 'application/json'
}
response = requests.post(url, headers=headers, data=json.dumps(data))

print(f"Status: {response.status_code}")
print("Response:" , response.json())
