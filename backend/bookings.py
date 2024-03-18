from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
from os import environ
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/booking_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Bookings(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_email = db.Column(db.String(255), nullable=False)
    screening_id = db.Column(db.Integer, nullable=False)  
    seat_id = db.Column(db.JSON, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Added quantity field
    booking_status = db.Column(db.Enum('Pending', 'Confirmed', 'Refunded'), nullable=False, default='Pending')
    payment_transaction_id = db.Column(db.String(255))
    refund_transaction_id = db.Column(db.String(255))
    creation_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, user_email, screening_id, seat_id, quantity, booking_status='Pending', payment_transaction_id=None, refund_transaction_id=None, creation_timestamp=datetime.utcnow()):
        self.user_id = user_id
        self.user_email = user_email
        self.screening_id = screening_id
        self.seat_id = seat_id
        self.quantity = quantity
        self.booking_status = booking_status
        self.payment_transaction_id = payment_transaction_id
        self.refund_transaction_id = refund_transaction_id
        self.creation_timestamp = creation_timestamp    


    def json(self):
        return {
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "screening_id": self.screening_id,
            "seat_id": self.seat_id,
            "quantity": self.quantity,
            "booking_status": self.booking_status,
            "payment_transaction_id": self.payment_transaction_id,
            "refund_transaction_id": self.refund_transaction_id,
            "creation_timestamp": self.creation_timestamp.isoformat()
        }


# get all bookings
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


# create a booking record
@app.route("/bookings", methods=["POST"])
def create_booking():
    # print(request.data)
    # user_id = request.args.get("user_id")
    # email = request.args.get("email")
    # screening_id = request.args.get("screening_id")

    data = request.json
    user_id = data.get("user_id")
    user_email = data.get("user_email")
    screening_id = data.get("screening_id")

    if not all([user_id, user_email, screening_id, data]):
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
    
    quantity = len(seat_ids["seats"])

    new_booking = Bookings(user_id=user_id, user_email=user_email, screening_id=screening_id, seat_id=seat_ids, quantity=quantity, booking_status='Pending')
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({
        "code": 201,
        "message": "Booking created successfully.",
        "data": new_booking.json()
    }), 201


# get booking details by booking_id
@app.route("/bookings/<int:booking_id>", methods=["GET"])
def get_booking_details(booking_id):

    booking = db.session.scalars(db.select(Bookings).filter_by(booking_id=booking_id).limit(1)).first()

    if booking:
        return jsonify({
            "code": 200,
            "data": booking.json()
        }), 200
    else:
        return jsonify({
            "code": 404,
            "message": "Booking not found. Please check booking ID."
        }), 404


# update payment status in a booking
@app.route("/bookings/<int:booking_id>/confirm", methods=["PUT"])
def confirm_booking(booking_id):
    booking = Bookings.query.get(booking_id)

    if not booking or booking.booking_status == 'Confirmed':
        return jsonify({
            "code": 404,
            "message": "Booking not found or is already confirmed."
        }), 404

    try:
        payment_transaction_id = request.json.get("payment_transaction_id")

        if not payment_transaction_id:
            return jsonify({
                "code": 400,
                "message": "Payment transaction ID is required."
            }), 400

        booking.booking_status = 'Confirmed'
        booking.payment_transaction_id = payment_transaction_id

        db.session.commit()

        return jsonify({
            "code": 200,
            "message": "Booking status updated to Confirmed.",
            "data": booking.json()
        }), 200
    except:
        
        return jsonify({
            "code": 500,
            "message": "An error occurred while updating the booking status.",
            
        }), 500


# update refund status
@app.route("/bookings/<int:booking_id>/refund", methods=["PUT"])
def refund_booking(booking_id):
    booking = Bookings.query.get(booking_id)

    if not booking or booking.booking_status == 'Refunded':
        return jsonify({
            "code": 404,
            "message": "Booking not found or is already refunded."
        }), 404

    try:
        refund_transaction_id = request.json.get("refund_transaction_id")

        booking.booking_status = 'Refunded'
        booking.refund_transaction_id = refund_transaction_id

        db.session.commit()

        return jsonify({
            "code": 200,
            "message": "Booking status updated to Refunded.",
            "data": {
                "refund_transaction_id": refund_transaction_id,
                "booking": booking.json()
            }
        }), 200
    except:
        return jsonify({
            "code": 500,
            "message": "An error occurred while processing the refund. Please try again.",
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
