from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http
from os import environ

app = Flask(__name__)
CORS(app)

booking_URL_get_booking = environ.get('booking_URL_get_booking') or "http://127.0.0.1:5001/bookings/{booking_id}"
booking_URL_refund = environ.get('booking_URL_refund') or "http://127.0.0.1:5001/bookings/{booking_id}/refund"
seat_URL_release = environ.get('seat_URL_release') or "http://127.0.0.1:5000/manage_seats/{screening_id}/release"
transaction_URL_reverse = environ.get('transaction_URL_reverse') or "http://127.0.0.1:5004/transactions/{transaction_id}/reverse"

@app.route("/refund/<booking_id>", methods=['POST'])
def processRefund(booking_id):
    if request.is_json:
        try:
            refund_details = request.get_json()  
            result = initiateRefund(booking_id, refund_details)
            return jsonify(result)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
           

    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def initiateRefund(booking_id, refund_details):
    try:
        print('\n-----Invoking bookings microservice for refund-----')

        # Get booking details
        get_booking_URL = booking_URL_get_booking.format(booking_id=booking_id)
        booking_details = invoke_http(get_booking_URL, method='GET')

        # Extract necessary information
        screening_id = booking_details["data"]["screening_id"]
        transaction_id = booking_details["data"]["payment_transaction_id"]

        # Reverse payment transaction
        transaction_result = invoke_http(transaction_URL_reverse.format(transaction_id=transaction_id), method='PUT')
        print('Transaction reversal result:', transaction_result)

        # Update booking status to "Refunded"
        refund_booking_URL = booking_URL_refund.format(booking_id=booking_id)
        invoke_http(refund_booking_URL, method='PUT')

        # Release seats
        release_seats_URL = seat_URL_release.format(screening_id=screening_id)
        seat_release_result = invoke_http(release_seats_URL, method='PUT', json={"seats": booking_details["data"]["seat_id"]["seats"]})
        print('Seat release result:', seat_release_result)

        return {
            "code": 200,
            "message": "Refund processed successfully"
        }

    except Exception as e:
        print("An error occurred:", e)
        return {
            "code": 500,
            "message": "An error occurred while processing refund"
        }

if __name__ == "__main__":
    print("This is refund orchestrator...")
    app.run(host="0.0.0.0", port=5102, debug=True)  # Using a different port for refund orchestrator
