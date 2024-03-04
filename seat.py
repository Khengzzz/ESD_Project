from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/event_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Seat(db.Model):
    __tablename__ = 'seat'

    event_id = db.Column(db.Integer, nullable=False, primary_key=True)
    seat_id = db.Column(db.Integer, nullable=False, primary_key=True)
    seat_status = db.Column(db.Enum('available', 'booked', 'reserved', 'unavailable'), nullable=False, default='available')

    def __init__(self, event_id, seat_id, seat_status='available'):
        self.event_id = event_id
        self.seat_id = seat_id
        self.seat_status = seat_status

    def json(self):
        return {
            "event_id": self.event_id,
            "seat_id": self.seat_id,
            "seat_status": self.seat_status
        }




@app.route("/seats/<string:event_id>")
def get_all_seats(event_id):
    seat_list = Seat.query.filter_by(event_id=event_id).all()

    if seat_list:
        return jsonify({
            "code": 200,
            "data": {
                "seats": [seat.json() for seat in seat_list]
            }
        }), 200
    else:
        return jsonify({
            "code": 404,
            "message": f"There are no seats for the event."
        }), 404




@app.route("/reserveseats/<event_id>", methods=["PUT"])
def reserve_seats(event_id):
    data = request.json

    if not data or "seat_ids" not in data:
        return jsonify({
            "code": 400,
            "message": "No seat IDs provided."
        }), 400

    seat_ids = data["seat_ids"]

    if not seat_ids:
        return jsonify({
            "code": 400,
            "message": "No seat IDs provided."
        }), 400

    # Check if all seats are available
    for seat_id in seat_ids:
        seat = Seat.query.filter_by(event_id=event_id, seat_id=seat_id).first()

        if not seat or seat.seat_status != "available":
            return jsonify({
                "code": 400,
                "message": f"Seat {seat_id} is not available."
            }), 400

    # If all seats are available, reserve them
    for seat_id in seat_ids:
        seat = Seat.query.filter_by(event_id=event_id, seat_id=seat_id).first()
        seat.seat_status = "reserved"
        db.session.commit()

    return jsonify({
        "code": 200,
        "message": "Seats have been reserved."
    }), 200




@app.route("/bookseats/<event_id>", methods=["PUT"])
def book_seats(event_id):
    data = request.json

    if not data or "seat_ids" not in data:
        return jsonify({
            "code": 400,
            "message": "No seat IDs provided."
        }), 400

    seat_ids = data["seat_ids"]

    if not seat_ids:
        return jsonify({
            "code": 400,
            "message": "No seat IDs provided."
        }), 400

    # Check if all seats are reserved
    for seat_id in seat_ids:
        seat = Seat.query.filter_by(event_id=event_id, seat_id=seat_id).first()

        if not seat or seat.seat_status != "reserved":
            return jsonify({
                "code": 400,
                "message": f"Seat {seat_id} is not reserved."
            }), 400

    # If all seats are reserved, book them
    for seat_id in seat_ids:
        seat = Seat.query.filter_by(event_id=event_id, seat_id=seat_id).first()
        seat.seat_status = "booked"
        db.session.commit()

    return jsonify({
        "code": 200,
        "message": "Seats have been booked."
    }), 200




@app.route("/refundseats/<event_id>", methods=["PUT"])
def refund_seats(event_id):
    data = request.json

    if not data or "seat_ids" not in data:
        return jsonify({
            "code": 400,
            "message": "No seat IDs provided."
        }), 400

    seat_ids = data["seat_ids"]

    if not seat_ids:
        return jsonify({
            "code": 400,
            "message": "No seat IDs provided."
        }), 400

    # Check if all seats are booked
    for seat_id in seat_ids:
        seat = Seat.query.filter_by(event_id=event_id, seat_id=seat_id).first()

        if not seat or seat.seat_status != "booked":
            return jsonify({
                "code": 400,
                "message": f"Seat {seat_id} is not booked."
            }), 400

    # If all seats are booked, refund them
    for seat_id in seat_ids:
        seat = Seat.query.filter_by(event_id=event_id, seat_id=seat_id).first()
        seat.seat_status = "available"
        db.session.commit()

    return jsonify({
        "code": 200,
        "message": "Seats have been refunded."
    }), 200




if __name__ == '__main__':
    app.run(port=5001, debug=True)