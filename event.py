from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/event_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Event(db.Model):
    __tablename__ = 'event'

    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(255), nullable=False)
    event_description = db.Column(db.Text, nullable=False)
    event_date_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    event_status = db.Column(db.Enum('active', 'cancelled'), nullable=False, default='active')
    ticket_price = db.Column(db.Float(precision=2), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    creation_timestamp = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    def __init__(self, event_name, event_description, event_date_time, location, ticket_price, capacity):
        self.event_name = event_name
        self.event_description = event_description
        self.event_date_time = event_date_time
        self.location = location
        self.ticket_price = ticket_price
        self.capacity = capacity

    def json(self):
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "event_description": self.event_description,
            "event_date_time": self.event_date_time.isoformat(),
            "location": self.location,
            "event_status": self.event_status,
            "ticket_price": self.ticket_price,
            "capacity": self.capacity,
            "creation_timestamp": self.creation_timestamp.isoformat()
        }


@app.route("/events")
def get_all_events():
    event_list = Event.query.all()

    if event_list:
        return jsonify({
            "code": 200,
            "data": {
                "events": [event.json() for event in event_list]
            }
        }), 200
    else:
        return jsonify({
            "code": 404,
            "message": "There are no events."
        }), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)