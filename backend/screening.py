from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from os import environ
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root:root@localhost:3306/screening'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Screening(db.Model):
    __tablename__ = 'screening'

    screening_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_name = db.Column(db.String(255), nullable=False)
    movie_description = db.Column(db.String(255), nullable=False)
    movie_date_time = db.Column(db.DateTime, nullable=False)
    hall_number = db.Column(db.Integer, nullable=False)
    movie_status = db.Column(db.Enum('Now Showing', 'Coming Soon', 'Cancelled'), nullable=False, default='Now Showing')
    ticket_price = db.Column(db.Float(precision=2), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    creation_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, movie_name, movie_description, movie_date_time, hall_number, ticket_price, capacity):
        self.movie_name = movie_name
        self.movie_description = movie_description
        self.movie_date_time = movie_date_time
        self.hall_number = hall_number
        self.ticket_price = ticket_price
        self.capacity = capacity

    def json(self):
        return {
            "screening_id": self.screening_id,
            "movie_name": self.movie_name,
            "movie_description": self.movie_description,
            "movie_date_time": self.movie_date_time.isoformat(),
            "hall_number": self.hall_number,
            "movie_status": self.movie_status,
            "ticket_price": self.ticket_price,
            "capacity": self.capacity,
            "creation_timestamp": self.creation_timestamp.isoformat()
        }


class Seat(db.Model):
    __tablename__ = 'seat'

    screening_id = db.Column(db.Integer, nullable=False, primary_key=True)
    seat_id = db.Column(db.Integer, nullable=False, primary_key=True)
    seat_status = db.Column(db.Enum('available', 'booked', 'reserved', 'unavailable'), nullable=False, default='available')

    def __init__(self, screening_id, seat_id, seat_status='available'):
        self.screening_id = screening_id
        self.seat_id = seat_id
        self.seat_status = seat_status

    def json(self):
        return {
            "screening_id": self.screening_id,
            "seat_id": self.seat_id,
            "seat_status": self.seat_status
        }


# Get all screening details
@app.route("/screenings")
def get_all_screenings():
    screening_list = Screening.query.all()

    if screening_list:
        return jsonify({
            "code": 200,
            "data": {
                "screenings": [screening.json() for screening in screening_list]
            }
        }), 200
    else:
        return jsonify({
            "code": 404,
            "message": "There are no screenings."
        }), 404


# Get details from a screening
@app.route("/screenings/seats/<string:screening_id>")
def get_all_seats(screening_id):
    seat_list = Seat.query.filter_by(screening_id=screening_id).all()

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
            "message": f"There are no seats for the screening."
        }), 404


# Update seat status from a screening
@app.route("/screenings/manage_seats/<screening_id>/<type>", methods=["PUT"])
def manage_seats(screening_id, type):
    data = request.json

    if not data or "seats" not in data:
        return jsonify({
            "code": 400,
            "message": "No seat IDs provided."
        }), 400

    seat_ids = data["seats"]

    if not seat_ids:
        return jsonify({
            "code": 400,
            "message": "No seat IDs provided."
        }), 400

    valid_types = ["reserve", "book", "refund", "revert"]

    if type not in valid_types:
        return jsonify({
            "code": 400,
            "message": "Invalid operation type. Valid types are 'reserve', 'book', 'refund', and 'revert'."
        }), 400

    for seat_id in seat_ids:
        seat = Seat.query.filter_by(screening_id=screening_id, seat_id=seat_id).first()

        if not seat:
            return jsonify({
                "code": 400,
                "message": f"Seat {seat_id} does not exist for the specified screening."
            }), 400

        if type == "reserve":
            if seat.seat_status != "available":
                return jsonify({
                    "code": 400,
                    "message": f"Seat {seat_id} is not available for reservation."
                }), 400
            seat.seat_status = "reserved"

        elif type == "book":
            if seat.seat_status != "reserved":
                return jsonify({
                    "code": 400,
                    "message": f"Seat {seat_id} is not reserved and cannot be booked."
                }), 400
            seat.seat_status = "booked"

        elif type == "refund":
            if seat.seat_status != "booked":
                return jsonify({
                    "code": 400,
                    "message": f"Seat {seat_id} is not booked and cannot be refunded."
                }), 400
            seat.seat_status = "available"

        elif type == "revert":
            if seat.seat_status != "reserved":
                return jsonify({
                    "code": 400,
                    "message": f"Seat {seat_id} is not reserved and cannot be reverted."
                }), 400
            seat.seat_status = "available"

        db.session.commit()

    return jsonify({
        "code": 200,
        "message": f"Seats have been {type}ed successfully."
    }), 200





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)