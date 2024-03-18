from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http
from os import environ

import amqp_connection
import pika
import json

app = Flask(__name__)
CORS(app)

exchangename="payment_topic"
exchangetype="topic"

def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def check_exchange(channel, exchange_name, exchange_type):
    try:
        channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)
        return True
    except Exception as e:
        print("Error while declaring exchange:", e)
        return False

#connection = create_connection()
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()


#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

@app.route("/payment/<booking_id>", methods=['POST'])
def processPayment(booking_id):
    if request.is_json:
        try:
            charge_details = request.get_json()
            result = updateOrder(booking_id, charge_details)
            
            # Establish connection to RabbitMQ broker
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()

            # Declare the exchange if not already declared
            #channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype)

        
                # Payment success, publish message to payment.success queue
            print('\n\n-----Publishing the (payment success) message with routing_key=*.success-----')
            payment_details = {
                    #"booking_id": booking_id,
                "payment_transaction_id": charge_details["id"],
                "email": charge_details["billing_details"]["name"]
            }
            channel.basic_publish(exchange=exchangename, routing_key="*.success", body=json.dumps(payment_details))
            #else:
                # Payment failure, publish message to payment.error queue
                # error_details = {
                #     "booking_id": booking_id,
                #     "error_message": result["message"],
                #     "email": charge_details["billing_details"]["name"]
                # }
                # channel.basic_publish(exchange=exchangename, routing_key="payment.error", body=json.dumps(error_details))

            connection.close()

            return jsonify(result)

        except Exception as e:
            print(charge_details)
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
    seat_URL = environ.get('seat_URL') or "http://127.0.0.1:5000/screenings/manage_seats/{screening_id}/book"
    booking_URL_get_booking = environ.get('booking_URL_get_booking') or "http://127.0.0.1:5001/bookings/{booking_id}"
    booking_URL_confirm = environ.get('booking_URL_confirm') or "http://127.0.0.1:5001/bookings/{booking_id}/confirm"
    
    try:
        print('\n-----Invoking bookings microservice-----')

        # Get booking details
        get_booking_URL = booking_URL_get_booking.format(booking_id=booking_id)
        booking_details = invoke_http(get_booking_URL, method='GET')
        print("Booking details:", booking_details)

        # Extract necessary information from booking details
        screening_id = booking_details["data"]["screening_id"]
        seat_ids = booking_details["data"]["seat_id"]["seats"]  # Extract seat IDs from nested dictionary

        # Update seat status
        seat_url = seat_URL.format(screening_id=screening_id)
        seat_result = invoke_http(seat_url, method='PUT', json={"seats": seat_ids})
        print('Seat update result:', seat_result)

        # Confirm booking with payment transaction ID
        transaction_id = charge_details["id"]
        email = charge_details["billing_details"]["name"]
        booking_URL_confirm = booking_URL_confirm.format(booking_id=booking_id)
        booking_result = invoke_http(booking_URL_confirm, method='PUT', json={"booking_id": booking_id,
                                                                                "payment_transaction_id": transaction_id,
                                                                                "email": email})
        print('Booking confirmation result:', booking_result)

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
    app.run(host="0.0.0.0", port=5101, debug=True)
