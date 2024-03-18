from flask import Flask, render_template, request, jsonify,redirect,url_for
import stripe
import json
import requests
import datetime
from invokes import invoke_http
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from datetime import datetime
from os import environ
from flask_cors import CORS


app = Flask(__name__)
stripe.api_key = "sk_test_51OrGR4EaG7MlgHzNxoK8QmcdiOylptZTRcHBzmdyGpBSccw1suzZraVKcjFuQbH23ztdaABzUJIBn4w5EzRV9V8400rakKh75Q"

# Call from booking details

#link to db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/transactions'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Transactions(db.Model):
    transaction_id = db.Column(db.String(255), primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False)
    transaction_amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_status = db.Column(Enum('succeeded', 'refunded', name='transaction_status'), default='succeeded', nullable=False)
    payment_date_time = db.Column(db.DateTime, nullable=False)
    creation_date_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


#write to db method
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
# Call from booking
    

def getTicketQuantity(information):
    
    quantity=information['quantity']
    ticket_cost=1500
    total_amount= ticket_cost*quantity
    return total_amount

#get data from other microservice
testNewTransaction= 'http://127.0.0.1:5111/data'
# testRefund='http://127.0.0.1:5200/refundNo'
def callUrl(url):
      # Replace with actual address
    response = requests.get(url)

    if response.status_code == 200:
        information = response.json()
        print("information is:")
        print(information)
        print()
        # Use the received information here (e.g., render in a template)
        return information
    else:
        
        print(f"Error retrieving information: {response.status_code}")


#get charge_id from booking_id
def get_transaction_id_by_booking_id(booking_id):
# Query the database to get the transaction_id based on booking_id
    result = Transactions.query.filter_by(booking_id=booking_id).first()

# Check if a result was found
    if result:
        return result
    else:
        return None  


#convert to utc time
def convert_unix_to_utc(unix_timestamp):
    utc_datetime = datetime.utcfromtimestamp(unix_timestamp)
    return utc_datetime

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




# payment portal to make payment
@app.route('/transactions/payment_portal')
def index():
    #information=callUrl(testNewTransaction)
    information = {
                    "quantity": 2,
                    "booking_id": 3
                    }

    amount=getTicketQuantity(information)
    booking_id=information["booking_id"]
    return render_template('index.html',total_amount=amount,booking_id=booking_id)


# create a charge object and calls payment orchestrator
@app.route('/transactions/charge', methods=['POST'])
def charge():
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
    current_time_utc=convert_unix_to_utc(unix_timestamp)
    print(charge_id)
    print(amount)
    print(booking_id)

    new_transaction =add_transaction_to_database(charge_id,booking_id,amount,current_time_utc)
    db.session.add(new_transaction)
    db.session.commit()
    
    #json data format and send
    payment_orch_url = environ.get('payment_orchestrator_URL') or "http://127.0.0.1:5101//payment/{booking_id}"
    payment_orch_url = payment_orch_url.format(booking_id=booking_id)
    
    send_status_result = invoke_http(payment_orch_url, method='POST', json=charge_object )
    
    if send_status_result:
        return render_template('success.html',charge_details=charge_object)
    
    else:
        return render_template('success.html',charge_details=charge_object)

#for testing purposes
@app.route("/transactions/refund-test")
def refund_test():
    return render_template('refund-test.html')


#refund json
@app.route("/transactions/refund/<booking_id>",methods=["POST"])
def refund_no_ui(booking_id):
    refund_orchestrator_url = environ.get('refund_orchestrator_URL') or "http://127.0.0.1:5102/refund/{booking_id}"
    refund_orchestrator_url = refund_orchestrator_url.format(booking_id=booking_id)

    transaction = Transactions.query.filter_by(booking_id=booking_id).first()
    
    refund = refund_charge(transaction.transaction_id)
    if refund:
        print("hi")
        transaction.transaction_status = 'refunded'
        db.session.commit()

        # return json of refund id
        send_status_result = invoke_http(refund_orchestrator_url, method='PUT', json={transaction })
        return jsonify({"refund_id": refund.id}), 200
    else:
        return jsonify({"error": "Refund failed"}), 500
    




@app.route("/transactions/refund/<charge_id>", methods=['POST'])
def refund(charge_id):
    # Call refund_charge function to initiate refund
    refund = refund_charge(charge_id)
    if refund:
        # Refund successful, redirect to success page or render success template
        return redirect(url_for('/transactions/refund_success', refund_id=refund.id))
    else:
        # Refund failed, redirect to error page or render error template
        return redirect(url_for('error'))




@app.route("/transactions/success")
def success():
    charge_id = request.args.get('charge_id')
    charge_object = retrieve_charge(charge_id)
    return render_template("success.html", charge_object=charge_object)




@app.route("/transactions/refund_success/<refund_id>")
def refund_success(refund_id):
    # Retrieve the refund object using the refund_id
    refund = retrieve_refund(refund_id)
    if refund:
        return render_template("refund_success.html", refund=refund)
    else:
        return render_template("error.html", message="Refund not found")




@app.route("/transactions/error")
def error():
    return render_template("error.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)