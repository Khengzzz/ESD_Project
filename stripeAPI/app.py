from flask import Flask, render_template, request, jsonify,redirect,url_for
import stripe
import json
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from datetime import datetime

app = Flask(__name__)
stripe.api_key = "sk_test_51OrGR4EaG7MlgHzNxoK8QmcdiOylptZTRcHBzmdyGpBSccw1suzZraVKcjFuQbH23ztdaABzUJIBn4w5EzRV9V8400rakKh75Q"

# Call from booking details

#link to db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/transactions'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Transaction(db.Model):
    transaction_id = db.Column(db.String(255), primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False)
    transaction_amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_status = db.Column(Enum('succeeded', 'refunded', name='transaction_status_enum'), default='succeeded', nullable=False)
    payment_date_time = db.Column(db.DateTime, nullable=False)
    creation_date_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# Call from booking
    
def getBookingId(bookingId):
    #call booking, retrieve booking id to get charge id
    placeholderJson=bookingId

    #then return charge id
    charge_id=""
    return charge_id

def getTicketQuantity():
    #ticketAmount calls from request

    #placeholder quantity val
    quantity=2
    ticket_cost=1500
    total_amount= ticket_cost*quantity
    return total_amount


# Stripe charge functions
def retrieve_charge(charge_id):
    try:
        charge = stripe.Charge.retrieve(charge_id)
        return charge
    except stripe.error.InvalidRequestError as e:
        # Handle the error, such as charge not found
        return None

def refund_charge(charge_id):
    try:
        refund = stripe.Refund.create(
            charge=charge_id
        )
        return refund
    except stripe.error.InvalidRequestError as e:
        # Handle the error, such as charge not found
        return None

def retrieve_refund(refund_id):
    try:
        refund = stripe.Refund.retrieve(refund_id)
        return refund
    except stripe.error.InvalidRequestError as e:
        # Handle the error, such as refund not found
        return None

# app routes
@app.route('/')
def index():

    amount=getTicketQuantity()
    return render_template('index.html',total_amount=amount)

@app.route('/charge', methods=['POST'])



def charge():
    token = request.form.get('stripeToken')
    amount=getTicketQuantity()
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
    charge_details = retrieve_charge(charge.id)

    # Pass charge_details to the success template
    return redirect(url_for('success', charge_id=charge.id))




@app.route("/refund/<charge_id>", methods=['POST'])
def refund(charge_id):
    # Call refund_charge function to initiate refund
    refund = refund_charge(charge_id)
    if refund:
        # Refund successful, redirect to success page or render success template
        return redirect(url_for('refund_success', refund_id=refund.id))
    else:
        # Refund failed, redirect to error page or render error template
        return redirect(url_for('error'))




@app.route("/success")
def success():
    charge_id = request.args.get('charge_id')
    charge_details = retrieve_charge(charge_id)
    return render_template("success.html", charge_details=charge_details)




@app.route("/refund_success/<refund_id>")
def refund_success(refund_id):
    # Retrieve the refund object using the refund_id
    refund = retrieve_refund(refund_id)
    if refund:
        return render_template("refund_success.html", refund=refund)
    else:
        return render_template("error.html", message="Refund not found")




@app.route("/error")
def error():
    return render_template("error.html")

if __name__ == "__main__":
    app.run(debug=True)
