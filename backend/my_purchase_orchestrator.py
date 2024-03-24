from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http
from os import environ
import json

app = Flask(__name__)
CORS(app)

# Route handler to retrieve the purchase list of a particular user
@app.route("/purchase/<user_id>", methods=['GET'])
def retrieve_purchase(user_id):

    user_booking_URL = environ.get('user_booking_URL') or "http://127.0.0.1:5001/bookings/user/{user_id}"
    try:
        # Retrieving all the bookings from a user 
        print('\n-----Invoking booking microservice-----')
        user_booking_URL = user_booking_URL.format(user_id=user_id)
        bookings = invoke_http(user_booking_URL,method="GET")

        purchase_list = []
        idx = 0

        # Going through each booking to retrieve the screening details
        for screening in bookings["data"]:
            screening_details_URL = environ.get('screening_details_URL') or "http://127.0.0.1:5000/screenings/{screening_id}"
            screening_details_URL = screening_details_URL.format(screening_id=screening["screening_id"])
            details = invoke_http(screening_details_URL,method="GET")

            # Adding seat_id and booking_id into the screening details and append into purchase_list
            seat_id = screening["seat_id"]["seats"]
            details["data"]["seats"][0]["seat_id"] = seat_id
            details["data"]["seats"][0]["booking_id"] = screening["booking_id"]
            details["data"]["seats"][0]["transaction_id"] = screening["transaction_id"]
            purchase_list.append(details)
            idx += 1
            
        return purchase_list

    except Exception as e:
        print("An error occurred:", e)
        return {
            "code": 500,
            "message": "An error occurred while booking. Please try again."
        }

if __name__ == "__main__":
    print("This is booking orchestrator...")
    app.run(host="0.0.0.0", port=5103, debug=True)