from ultralytics import YOLOWorld # type: ignore
import cv2
import requests
from datetime import datetime
import uuid

# Replace with actual GPS location retrieval or mock for testing
def get_current_location():
    # Example: return dummy coordinates or integrate with GPS hardware/API
    return -23.5505, -46.6333  # São Paulo coordinates as example

model = YOLOWorld('yolov8s-world.pt')

#Prompts
model.set_classes(['corrosion','fallen tree on power line','fire closed to a power line','downed power line','insulation on a power line'])

#Opened Camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

#Detection
results = model.predict(frame, conf=0.5)

#Detected?
for r in results:
    for name in r.names.values():
        print(f"Detected:{name}")

        # Drone Location
        latitude, longitude = get_current_location()

        # Alerts
        alert_data = {
            "uuid": str(uuid.uuid4()),
            "drone_id": "drone_123",  # Replace with actual drone ID
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "alert_type": name,
            "description": f"Detection of {name} via YOLO-World",
            "severity": "High",
            "latitude": latitude,     # Use actual location
            "longitude": longitude    # Use actual location
        }
        
        # Sending Alert
        try:
            response = requests.post("http://127.0.0.1:5000/add_alert", json=alert_data)
            print("Status:", response.status_code, "→", response.json())
        except Exception as e:
            print("Error during alert message sending:", e)

# Shown Video
    if frame is not None and frame.size != 0:
        cv2.imshow('YOLO Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
