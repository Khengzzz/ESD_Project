from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/booking_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Bookings(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    seat_id = db.Column(db.JSON, nullable=False)
    booking_status = db.Column(db.Enum('Pending', 'Confirmed', 'Refunded'), nullable=False, default='Pending')
    payment_transaction_id = db.Column(db.String(255))
    payment_status = db.Column(db.Enum('Succeeded', 'Pending', 'Failed'))
    refund_transaction_id = db.Column(db.String(255))
    creation_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, event_id, seat_id, booking_status, payment_transaction_id, payment_status, refund_transaction_id, creation_timestamp):
        self.user_id = user_id
        self.event_id = event_id
        self.seat_id = seat_id
        self.booking_status = booking_status
        self.payment_transaction_id = payment_transaction_id
        self.payment_status = payment_status
        self.refund_transaction_id = refund_transaction_id
        self.creation_timestamp = creation_timestamp
        # booking id not included as it is auto incremented

    def json(self):
        return {
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "seat_id": self.seat_id,
            "booking_status": self.booking_status,
            "payment_transaction_id": self.payment_transaction_id,
            "payment_status": self.payment_status,
            "refund_transaction_id": self.refund_transaction_id,
            "creation_timestamp": self.creation_timestamp.isoformat()
        }
    
@app.route("/bookings")
def get_all_bookings():
    booking_list = Bookings.query.all()
    if booking_list:
        return jsonify({
            "code": 200,
            "data": {
                "bookings": [booking.json() for booking in booking_list]
            }
        }), 200
    else:
        return jsonify({
            "code": 404,
            "message": "There are no bookings."
        }), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
