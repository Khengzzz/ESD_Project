from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http
from os import environ
import json
import amqp_connection
import pika

app = Flask(__name__)
CORS(app)

exchangename="notification"
exchangetype="topic"

def create_connection():
    return pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def check_exchange(channel, exchangename, exchangetype):
    try:
        channel.exchange_declare(exchange=exchangename, exchangetype=exchangetype, durable=True)
        return True
    except Exception as e:
        print("Error while declaring exchange:", e)
        return False

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

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
    seat_URL = environ.get('seat_URL') or "http://127.0.0.1:5000/screenings/seats/{screening_id}"
    refund_seat_URL = environ.get('refund_seat_URL') or "http://127.0.0.1:5000/screenings/manage_seats/{screening_id}/refund"
    booking_URL_get_booking = environ.get('booking_URL_get_booking') or "http://127.0.0.1:5001/bookings/{booking_id}"
    booking_URL_refund = environ.get('booking_URL_refund') or "http://127.0.0.1:5001/bookings/{booking_id}/refund"
    subscriber_URL = environ.get('subscriber_URL') or "http://127.0.0.1:5003/subscriptions/{screening_id}"

    try:
        print('\n-----Invoking bookings microservice for refund-----')

        # Get booking details
        booking_URL_get_booking = booking_URL_get_booking.format(booking_id=booking_id)
        booking_details = invoke_http(booking_URL_get_booking, method='GET')
        
        # Retrieve the email and payment transaction id of the person who refunded
        refund_user_email = booking_details["data"]["user_email"]
        refund_payment_transaction_id = booking_details["data"]["payment_transaction_id"]

        # Extract necessary information
        screening_id = booking_details["data"]["screening_id"]

        # Update booking status to "Refunded" and include refund id
        transaction_id = refund_details["id"]
        booking_URL_refund = booking_URL_refund.format(booking_id=booking_id)
        refund_result = invoke_http(booking_URL_refund, method='PUT', json={"booking_id": booking_id,
                                                                                "refund_transaction_id": transaction_id})
        print('Booking refund result:', refund_result)

        # Check screening capcacity
        seat_URL = seat_URL.format(screening_id=screening_id)
        seat_results = invoke_http(seat_URL, method='GET')
        seat_available = False

        for seat in seat_results['data']['seats']:
            if seat['seat_status'] == 'available':
                seat_available = True
                break  # Exit loop as soon as one available seat is found

        # Change seat status to available
        refund_seat_URL = refund_seat_URL.format(screening_id=screening_id)
        seat_release_result = invoke_http(refund_seat_URL, method='PUT', json={"seats": booking_details["data"]["seat_id"]["seats"]})
        print('Seat release result:', seat_release_result)

        # Get a list of subscribers if the screening capacity is full and a user refunds seat(s)
        if seat_available == False:
            subscriber_URL = subscriber_URL.format(screening_id=screening_id)
            subscribers = invoke_http(subscriber_URL, method='GET')
            print("Subscribers:", subscribers)
            
            # Retrieving user_email values and appending them to email_list
            email_list = [subscriber['user_email'] for subscriber in subscribers['data']['subscribers']]
    
            # Refund success, publish message to new ticket queue informing subscribers that there are slots
            print('\n\n-----Publishing the (subscriber notif) message with routing_key=*.subscribers-----')
            subscriber_notif_details = {
                "booking_id": booking_id,
                "screening_id": screening_id,
                "email": ",".join(email_list)
            }
            channel.basic_publish(exchange=exchangename, routing_key="*.subscribers", body=json.dumps(subscriber_notif_details))
            
            # Refund success, publish message to refund queue informing refund is successful
            print('\n\n-----Publishing the (refund success) message with routing_key=*.refund-----')
            refund_details = {
                "booking_id": booking_id,
                "payment_transaction_id": refund_payment_transaction_id,
                "screening_id": screening_id,
                "email": refund_user_email
            }
            channel.basic_publish(exchange=exchangename, routing_key="*.refund", body=json.dumps(refund_details))
        
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
    app.run(host="0.0.0.0", port=5102, debug=True)
