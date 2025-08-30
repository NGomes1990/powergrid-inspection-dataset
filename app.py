from flask import Flask, render_template, Response, request, jsonify
import flask
from flask_sqlalchemy import SQLAlchemy # type: ignore
from datetime import datetime
import uuid
from camera import VideoCamera

app = Flask(__name__)

alerts = []

monitored_classes = [
    'corrosion on power line',
    'intrusion on power line',
    'fallen tree on power line',
    'downed power line',
    'insulation on a power line',
    'fire closed to a power line',
    'broken power line',
    'power line maintenance',
]


#DbConfig
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alerts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#AlertMode
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    drone_id = db.Column(db.String(50))
    timestamp = db.Column(db.String(50))
    alert_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    severity = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

#Camera
camera = VideoCamera(0,'yolov8s-world.pt')

#Dashboard
@app.route('/')
def index():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
    return render_template('alerts.html', alerts=alerts)

#VideoFeed
def generate_frames(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield(b'--frame\r\n'
                  b'Content-type:image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            break
                    
@app.route('/video_feed')
def video():
    return Response(generate_frames(camera),
                    mimetype='multipart/x-mixed-replace;boundary=frame')

#JsonAlerts
@app.route('/add_alert', methods=['POST'])
def add_alert():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'error': 'Invalid data'}), 400
    alert = Alert(
        drone_id=data.get('drone_id'),
        timestamp=data.get('timestamp',datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')),
        alert_type=data.get('alert_type'),
        description=data.get('description'),
        severity=data.get('severity'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify({'message':'Alert added successfully', 'uuid': alert.uuid}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
        
        