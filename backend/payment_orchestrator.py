from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

seat_URL = "http://127.0.0.1:5000/manage_seats/{screening_id}/book"
booking_URL_get_booking = "http://127.0.0.1:5001/bookings/{booking_id}"
booking_URL_confirm = "http://127.0.0.1:5001/bookings/{booking_id}/confirm"

@app.route("/payment/<booking_id>", methods=['POST'])
def processPayment(booking_id):
    if request.is_json:
        try:
            charge_details = request.get_json()
            result = updateOrder(booking_id, charge_details)
            return jsonify(result)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "payment_orchestrator.py internal error: " + ex_str
            }), 500

    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def updateOrder(booking_id, charge_details):
    try:
        print('\n-----Invoking bookings microservice-----')

        get_booking_URL = booking_URL_get_booking.format(booking_id=booking_id)
        booking_details = invoke_http(get_booking_URL, method='GET')

        screening_id = booking_details["data"]["screening_id"]
        seat_ids = booking_details["data"]["seat_id"]

        seat_url = seat_URL.format(screening_id=screening_id)
        seat_result = invoke_http(seat_url, method='PUT', json={"seat_ids": seat_ids})
        print('result:', seat_result)


        transaction_id = charge_details["id"]
        confirm_booking_URL = booking_URL_confirm.format(booking_id=booking_id)
        booking_result = invoke_http(confirm_booking_URL, method='PUT', json={"booking_id": booking_id,
                                                                                "payment_transaction_id": transaction_id})
        print('booking result:', booking_result)

        return {
            "code": 200,
            "message": "Payment processed successfully"
        }

    except Exception as e:
        print("An error occurred:", e)
        return {
            "code": 500,
            "message": "An error occurred while processing payment"
        }


if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
        " for changing the seat...")
    app.run(host="0.0.0.0", port=5100, debug=True)
