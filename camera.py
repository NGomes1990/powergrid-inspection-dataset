import uuid
import cv2 # type: ignore
from ultralytics import YOLOWorld
from datetime import datetime
import json
import requests
import random


class VideoCamera:
    def __init__(self, source=0, model_path='YOLOWorld'):
        self.cap = cv2.VideoCapture(source)
        self.model = YOLOWorld('yolov8s-world.pt')
        self.drone_id = "drone123"  # Example drone ID

        self.monitored_classes = [
            'corrosion on power line',
            'intrusion on power line',
            'fallen tree on power line',
            'downed power line',
            'insulation on a power line',
            'fire closed to a power line',
            'broken power line',
            'power line maintenance',
        ]


    def __del__(self):
        self.cap.release()


    def classify_severity(self, label):
        # Simple classification logic based on label
        if label in ['fallen tree on power line', 'fire closed to a power line', 'broken power line', 'downed power line']:
            return 'High'
        elif label in ['insulation on a power line', 'corrosion on power line', 'intrusion on a power line']:
            return 'Medium'
        else:
            return 'Low'

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:

            return None

        results = self.model(frame)[0]
        classes = results.names
        detected_classes = results.boxes.cls.tolist()
        annotated_frame = results.plot()

        for class_id in detected_classes:
            class_name = classes[int(class_id)]

            # Only send alerts if in monitored_classes
            if class_name in self.monitored_classes:
                self.send_alert(class_name, annotated_frame)

                # Return the frame for video stream
        _, jpeg = cv2.imencode('.jpg', annotated_frame)
        return jpeg.tobytes()


    def send_alert(self, label, annotated_frame):
        severity = self.classify_severity(label)
        data = {
            "uuid": str(uuid.uuid4()),
            "drone_id": "drone123",
                "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "alert_type": label,
                "description": f"Detected {label} in the area.",
                "severity": severity,
                "latitude": random.uniform(-90, 90),  # Random latitude
                "longitude": random.uniform(-180, 180)  # Random longitude
            }

        try:
            requests.post('http://127.0.0.1:5000/add_alert', json=data)
        except Exception as e:
            print(f"Error sending alert: {e}")

            
            
       
