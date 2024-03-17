from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http
from os import environ

app = Flask(__name__)
CORS(app)

screening_URL_reserve = environ.get('screening_URL_reserve') or "http://127.0.0.1:5000/manage_seats/{screening_id}/reserve"
booking_URL_create = environ.get('booking_URL_create') or "http://127.0.0.1:5001/bookings"
# booking_URL_get_booking = environ.get('booking_URL_get_booking') or "http://127.0.0.1:5001/bookings/{booking_id}"

@app.route("/receive_booking", methods=['POST'])
def receivebooking():
    if request.is_json:
        try:
            booking_details = request.get_json() #assuming that data fields: user_id, email, screening_id, seat_id are sent in a json file
            print("\nReceived booking details in JSON:", booking_details)

            # 1. Send booking details from UI to booking orchestrator 
            result = processBooking(booking_details) #link to process booking fn/route
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "booking_orchestrator.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processBooking(booking_details):
    try:

        # 2. interact with screening.py to update seat status to reserve - orchestrator runs but reserve status in db is not updated
        print('\n-----Invoking screening microservice-----')
        # print(booking_details["screening_id"])
        reserve_seats_URL = screening_URL_reserve.format(screening_id=booking_details["screening_id"])
        invoke_http(reserve_seats_URL, method='PUT', json=booking_details)
        print("\nSeats are reserved")

        # 3. send booking details to booking.py to create new entry
        print('\n-----Invoking booking microservice-----')
        result = invoke_http(booking_URL_create,method="POST", json=booking_details)
        # have not accounted for error here, continues even if invocation fails
        # print(result)
        print("\nBooking details sent to booking microservice.\n")
        

        # 4. booking.py returns details to booking orchestrator 
        if result.get('code') == 201:
            booking_response = result
            print("\nBooking details received from booking microservice:", booking_response)
            return {
                "code": 200,
                "message": "Booking successfully created",
                "booking_details": booking_response  # Return the booking details to the caller
            }
        else:
            print("\nFailed to create booking:", result.text)
            return {
                "code": result.status_code,
                "message": "Failed to create booking"
            }


    except Exception as e:
        print("An error occurred:", e)
        return {
            "code": 500,
            "message": "An error occurred while booking. Please try again."
        }

if __name__ == "__main__":
    print("This is booking orchestrator...")
    app.run(host="0.0.0.0", port=5103, debug=True) 
    # used 5103, different port 