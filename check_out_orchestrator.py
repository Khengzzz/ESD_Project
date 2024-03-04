from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)




@app.route("/check_out/<event_id>/<user_id>", methods=['POST'])
def check_out(event_id, user_id):
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            order = request.get_json()
            print("\nReceived a list of seats in JSON:", order)

            # do the actual work
            # 1. Send order info {cart items}
            result = process_check_out(order, event_id, user_id)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "check_out_orchestrator.py internal error: " + ex_str
            }), 500


    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400



def process_check_out(order, event_id, user_id):
    # 2. Send the order info {cart items}
    # Construct the URL with event_id and user_id
    booking_management_url = f"http://localhost:5000/bookings?user_id={user_id}&event_id={event_id}"
    
    print('\n-----Invoking booking management microservice-----')
    order_result = invoke_http(booking_management_url, method='POST', json=order)
    print('order_result:', order_result)
    
    # Check if order_result is None
    if order_result is None:
        return {
            "code": 500,
            "message": "Internal server error: booking management response is None"
        }

    seat_url = f"http://localhost:5001/reserveseats/{event_id}"
    print('\n-----Invoking seat microservice-----')
    seat_result = invoke_http(seat_url, method='PUT', json=order)
    print('seat_result:', seat_result)
    
    # Check if seat_result is None
    if seat_result is None:
        return {
            "code": 500,
            "message": "Internal server error: Unable to reserve seat"
        }
    
    return {
        "code": 200,
        "message": "Checkout successful"
    }




if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
        " for checking out movie ticket(s)")
    app.run(host="0.0.0.0", port=5100, debug=True)
