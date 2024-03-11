from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

seat_URL = "http://127.0.0.1:5000/manage_seats/{screening_id}/book"
booking_URL = "http://127.0.0.1:5001/bookings/{booking_id}/confirm"

@app.route("/payment/<screening_id>/<booking_id>", methods=['POST'])
def processPayment(screening_id, booking_id):
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            data = request.get_json()

            print("\nReceived screening ID:", screening_id)
            print("Received seat IDs:", data)

            result = updateOrder(screening_id, data, booking_id)
            return jsonify(result)

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "payment_orchestrator.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def updateOrder(screening_id, data, booking_id):
    try:
        # 2. Send the order info {cart items}
        # Invoke the seat microservice
        print('\n-----Invoking seat microservice-----')
        # Send request to seat microservice
        seat_ids = data["seat_ids"]
        seat_url = seat_URL.format(screening_id=screening_id)
        seat_result = invoke_http(seat_url, method='PUT', json={"seat_ids":seat_ids})
        print('result:', seat_result)

        # Send request to booking confirmation endpoint
        transaction_id = data["charge_details"]["id"]
        booking_url = booking_URL.format(booking_id=booking_id)
        booking_result = invoke_http(booking_url, method='PUT', json={"booking_id": booking_id,
                                                                        "payment_transaction_id": transaction_id})
        print('booking result:', booking_result)

        return {
            "code": 200,  # or the appropriate HTTP status code
            "message": "Payment processed successfully"
        }

    except Exception as e:
        # Log the exception
        print("An error occurred:", e)
        return {
            "code": 500,
            "message": "An error occurred while processing payment"
        }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
        " for changing the seat...")
    app.run(host="0.0.0.0", port=5100, debug=True)
