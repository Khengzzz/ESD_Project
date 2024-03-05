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

    def __init__(self, user_id, event_id, seat_id, booking_status='Pending', payment_transaction_id=None, payment_status=None, refund_transaction_id=None, creation_timestamp=datetime.utcnow()):
        self.user_id = user_id
        self.event_id = event_id
        self.seat_id = seat_id
        self.booking_status = booking_status
        self.payment_transaction_id = payment_transaction_id
        self.payment_status = payment_status
        self.refund_transaction_id = refund_transaction_id
        self.creation_timestamp = creation_timestamp


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



#when booking is first created, booking status will be pending
@app.route("/bookings", methods=["POST"])
def create_booking():
    user_id = request.args.get("user_id")
    event_id = request.args.get("event_id")
    data = request.json

    if not all([user_id, event_id, data]):
        return jsonify({
            "code": 400,
            "message": "Incomplete data provided."
        }), 400

    seat_ids = data.get("seat_ids")

    if not seat_ids:
        return jsonify({
            "code": 400,
            "message": "No seat IDs provided."
        }), 400

    new_booking = Bookings(user_id=user_id, event_id=event_id, seat_id=seat_ids, booking_status='Pending')
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({
        "code": 201,
        "message": "Booking created successfully.",
        "data": new_booking.json()
    }), 201

# payment is successful --> booking is successful, record is updated - to test
@app.route("/bookings/<int:booking_id>/success", methods=["PUT"])
def update_booking_success(booking_id):
    booking = Bookings.query.get(booking_id)

    if not booking:
        return jsonify({
            "code": 404,
            "message": "Booking not found."
        }), 404

    data = request.json

    if not data or "payment_transaction_id" not in data:
        return jsonify({
            "code": 400,
            "message": "Payment transaction ID is missing."
        }), 400

    payment_transaction_id = data.get("payment_transaction_id")

    booking.payment_transaction_id = payment_transaction_id
    booking.booking_status = "Confirmed"
    booking.payment_status = "Succeeded"

    db.session.commit()

    return jsonify({
        "code": 200,
        "message": "Booking status updated successfully.",
        "data": booking.json()
    }), 200

# refund requested - to test
@app.route("/bookings/<int:booking_id>/refund/request", methods=["PUT"])
def request_refund(booking_id):
    booking = Bookings.query.get(booking_id)

    if not booking:
        return jsonify({
            "code": 404,
            "message": "Booking not found."
        }), 404

    if booking.booking_status != "Confirmed":
        return jsonify({
            "code": 400,
            "message": "Refund can only be requested for confirmed bookings."
        }), 400

    booking.booking_status = "Pending"
    booking.payment_status = "Pending"  
    # need to include refund id --> to generate since we do not have a pre defined data for that for each refund

    db.session.commit()

    return jsonify({
        "code": 200,
        "message": "Refund requested successfully.",
        "data": booking.json()
    }), 200


# refund processed and is successful - to test
@app.route("/bookings/<int:booking_id>/refund/success", methods=["PUT"])
def confirm_refund(booking_id):
    booking = Bookings.query.get(booking_id)

    if not booking:
        return jsonify({
            "code": 404,
            "message": "Booking not found."
        }), 404

    if booking.booking_status != "Pending":
        return jsonify({
            "code": 400,
            "message": "Refund can only be confirmed for bookings with pending refunds. Please request for a refund first."
        }), 400

    refund_transaction_id = request.json.get("refund_transaction_id")  
    booking.refund_transaction_id = refund_transaction_id #to retrieve from point of request, above route

    booking.booking_status = "Successful"
    booking.payment_status = "Refunded"

    db.session.commit()

    return jsonify({
        "code": 200,
        "message": "Refund successful.",
        "data": booking.json()
    }), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)
