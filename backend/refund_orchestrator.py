from flask import Flask, render_template, request, jsonify,redirect,url_for
import stripe
from flask_cors import CORS
import sys
from invokes import invoke_http
from os import environ
import json
import amqp_connection
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from datetime import datetime
from prometheus_flask_exporter import PrometheusMetrics

# Link to db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/transactions'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
stripe.api_key = "sk_test_51OoQM4Db6e0xe0n3x00YdJ2FapLr7NZ9XTms5vOb6z64T38InsHjHOjaguKcESoNPCZZ0R225k4PU08aRQFteyA200kQwXA8r3"

metrics = PrometheusMetrics(app)

db = SQLAlchemy(app)
CORS(app)

# Transactions db and table
class Transactions(db.Model):
    transaction_id = db.Column(db.String(255), primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False)
    transaction_amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_status = db.Column(Enum('succeeded', 'refunded', name='transaction_status'), default='succeeded', nullable=False)
    payment_date_time = db.Column(db.DateTime, nullable=False)
    creation_date_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

exchangename="notification"
exchangetype="topic"

# Function to create refund object using Stripe API based on 'charge_id'
def refund_charge(charge_id):
    try:
        refund = stripe.Refund.create(
            charge=charge_id
        )
        return refund
    except stripe.error.InvalidRequestError as e:
        return None

# Create a connection and a channel to the broker to publish messages to activity_log, error queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)


# Route handler to handle refund requests, retrieves transaction details from the db,
# attempts to refund the charge using Stripe API and initiates the refund process
@app.route("/refund/<booking_id>", methods=['POST'])
def processRefund(booking_id):
    transaction = Transactions.query.filter_by(booking_id=booking_id).first()
    print("Transaction iss", transaction)
    refund = refund_charge(transaction.transaction_id)
    print("Refund iss", refund)
    if refund:
        transaction.transaction_status = 'refunded'
        db.session.commit()

        result = initiateRefund(booking_id, refund)
        return render_template('refund_success.html')

    return jsonify({"error": "Failed to process refund"})


# Function to initiate refund process, updates transaction status in the db, seat_status to 'Available',
# booking_status to 'Refunded', and notifies subscribers
def initiateRefund(booking_id, refund_details):
    seat_URL = environ.get('seat_URL') or "http://localhost:8000/screenings/seats/{screening_id}"
    refund_seat_URL = environ.get('refund_seat_URL') or "http://localhost:8000/screenings/manage_seats/{screening_id}/refund"
    booking_URL_get_booking = environ.get('booking_URL_get_booking') or "http://localhost:8000/bookings/{booking_id}"
    booking_URL_refund = environ.get('booking_URL_refund') or "http://localhost:8000/bookings/{booking_id}/refund"
    subscriber_URL = environ.get('subscriber_URL') or "http://localhost:8000/subscribers/subscriptions/{screening_id}"

    try:
        print('\n-----Invoking bookings microservice for refund-----')

        # Get booking details
        booking_URL_get_booking = booking_URL_get_booking.format(booking_id=booking_id)
        booking_details = invoke_http(booking_URL_get_booking, method='GET')
        
        # Extract necessary information
        refund_user_email = booking_details["data"]["user_email"]
        refund_payment_transaction_id = booking_details["data"]["payment_transaction_id"]
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
        print(seat_available)

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
    
            # Refund success, publish message with routing_key '*.subscribers' informing subscribers for the particular screening
            # that there are seats available
            print('\n\n-----Publishing the (subscriber notif) message with routing_key=*.subscribers-----')
            subscriber_notif_details = {
                "screening_id": screening_id,
                "email": ",".join(email_list)
            }
            channel.basic_publish(exchange=exchangename, routing_key="*.subscribers", body=json.dumps(subscriber_notif_details))
            
            # Refund success, publish message with routing_key '*.refund' informing refunder that their refund is successful
            print('\n\n-----Publishing the (refund success) message with routing_key=*.refund-----')
            refund_details = {
                "booking_id": booking_id,
                "payment_transaction_id": refund_payment_transaction_id,
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
    app.run(host="0.0.0.0", port=5102, debug=False)