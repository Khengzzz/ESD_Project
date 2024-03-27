from flask import Flask, render_template, request, jsonify,redirect,url_for
from flask_cors import CORS
import sys
from invokes import invoke_http
from os import environ
import stripe
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from datetime import datetime
import amqp_connection
from prometheus_flask_exporter import PrometheusMetrics

exchangename="notification"
exchangetype="topic"

connection = amqp_connection.create_connection()
channel = connection.channel()

# If the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)

# Link to db
app = Flask(__name__)
stripe.api_key = "sk_test_51OrGR4EaG7MlgHzNxoK8QmcdiOylptZTRcHBzmdyGpBSccw1suzZraVKcjFuQbH23ztdaABzUJIBn4w5EzRV9V8400rakKh75Q"
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/transactions'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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


# Function to add a new transaction to Transactions db
def add_transaction_to_database(transaction_id,booking_id, transaction_amount, payment_date_time):
# Create an instance of the Transaction model
    new_transaction = Transactions(
    transaction_id=transaction_id,
    booking_id=booking_id,
    transaction_amount=transaction_amount,
    transaction_status="succeeded",
    payment_date_time=payment_date_time
)
    return new_transaction

# Function to retrieve a Stripe charge by 'charge_id'
def retrieve_charge(charge_id):
    try:
        charge = stripe.Charge.retrieve(charge_id)
        return charge
    except stripe.error.InvalidRequestError as e:
        # Handle the error, such as charge not found
        return None

# Route handler to render the payment portal page
@app.route('/payment', methods=["POST"])
def paymentPage():
    print("hi")
    information = {
                    "quantity": 3,
                    "booking_id": 31
                    }

    amount=information['quantity']*1500
    booking_id=information["booking_id"]
    # return(information)
    # return redirect(url_for('success', total_amount=amount))
    return render_template('payment.html',total_amount=amount,booking_id=booking_id)


# Route handler to handle payment processing, creates a charge object after payment complete, update seat and booking status, 
# and notifies consumers
@app.route("/payment/charge", methods=['POST'])
def processPayment():
    token = request.form.get('stripeToken')
    amount=request.form.get("amount")
    currency = request.form.get('currency')

    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            source=token,
            description="This is a test payment"
        )
    except stripe.error.CardError as e:
        return redirect(url_for('error'))

    # Retrieve the charge object
    charge_object = retrieve_charge(charge.id)
    charge_id=charge_object.id
    booking_id=request.form.get('booking_id')
    unix_timestamp=charge_object.created
    current_time_utc=datetime.utcfromtimestamp(unix_timestamp)

    new_transaction =add_transaction_to_database(charge_id,booking_id,amount,current_time_utc)
    db.session.add(new_transaction)
    db.session.commit()

    # Update seat status and booking details
    result = updateOrder(booking_id, charge_object)
    
    # Checks for both successful payment and order update before publishing payment success message
    if result and result.get('code') == 200:
        # Payment success, publish message to payment.success queue
        print('\n\n-----Publishing the (payment success) message with routing_key=*.success-----')
        payment_details = {
                #"booking_id": booking_id,
            "payment_transaction_id": charge_object["id"],
            "email": charge_object["billing_details"]["name"]
        }
        channel.basic_publish(exchange=exchangename, routing_key="*.success", body=json.dumps(payment_details))

    else:
        # Payment failure, publish message to payment.error queue
        error_details = {
            "booking_id": booking_id,
            "error_message": result["message"],
            "email": charge_object["billing_details"]["name"]
        }
        channel.basic_publish(exchange=exchangename, routing_key="*.error", body=json.dumps(error_details))

        connection.close()

    if result:
        return render_template('success.html',charge_details=charge_object)
    
    else:
        return render_template('error.html',charge_details=charge_object)

# Function to update seat and booking status after successful payment
def updateOrder(booking_id, charge_object):
    seat_URL = environ.get('seat_URL') or "http://127.0.0.1:5000/screenings/manage_seats/{screening_id}/book"
    booking_URL_get_booking = environ.get('booking_URL_get_booking') or "http://127.0.0.1:5001/bookings/{booking_id}"
    booking_URL_confirm = environ.get('booking_URL_confirm') or "http://127.0.0.1:5001/bookings/{booking_id}/confirm"
    
    try:
        print('\n-----Invoking bookings microservice-----')
        booking_URL_confirm = booking_URL_confirm.format(booking_id=booking_id)
        booking_details = invoke_http(booking_URL_confirm, method='PUT', json={"payment_transaction_id": charge_object["id"],
                                                                                "email": charge_object['billing_details']['name']})

        # Get booking details
        booking_URL_get_booking = booking_URL_get_booking.format(booking_id=booking_id)
        booking_details = invoke_http(booking_URL_get_booking, method='GET')
        print("Booking details:", booking_details)

        # Extract necessary information from booking details
        screening_id = booking_details["data"]["screening_id"]
        seat_ids = booking_details["data"]["seat_id"]["seats"]  # Extract seat IDs from nested dictionary

        # Update seat status
        seat_url = seat_URL.format(screening_id=screening_id)
        seat_result = invoke_http(seat_url, method='PUT', json={"seats": seat_ids})
        print('Seat update result:', seat_result)

        # Update booking status with payment transaction ID
        transaction_id = charge_object["id"]
        email = charge_object["billing_details"]["name"]
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

# Route handler to handle cancellation of a booking before payment, reverting the seats to 'Available' and booking status to 'Cancelled'
@app.route("/payment/cancel/<booking_id>", methods=['POST'])
def cancel_payment(booking_id):
    revert_seat_URL = environ.get('revert_seat_URL') or "http://127.0.0.1:5000/screenings/manage_seats/{screening_id}/revert"
    booking_URL_cancel = environ.get('booking_URL_cancel') or "http://127.0.0.1:5001/bookings/{booking_id}/cancel"
    
    try:
        print('\n-----Invoking bookings microservice-----')

        # Get booking details
        booking_URL_cancel = booking_URL_cancel.format(booking_id=booking_id)
        booking_details = invoke_http(booking_URL_cancel, method='PUT')
        print("Booking details:", booking_details)

        # Extract necessary information from booking details
        screening_id = booking_details["data"]["screening_id"]
        seat_ids = booking_details["data"]["seat_id"]["seats"]

        # Update seat status
        revert_seat_URL = revert_seat_URL.format(screening_id=screening_id)
        seat_result = invoke_http(revert_seat_URL, method='PUT', json={"seats": seat_ids})
        print('Seat update result:', seat_result)

        return {
            "code": 200,
            "message": "Revert processed successfully"
        }

    except Exception as e:
        print("An error occurred:", e)
        return {
            "code": 500,
            "message": "An error occurred while processing request"
        }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5101, debug=False)
