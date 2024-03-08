
from flask import Flask, render_template, request, jsonify
import stripe,sqlalchemy
import requests
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)


# url = 'http://127.0.0.1:5100/data'  # Replace with actual address
# response = requests.get(url)

# if response.status_code == 200:
#     information = response.json()
#     # Use the received information here (e.g., render in a template)
#     print(information)
# else:
    
#     print(f"Error retrieving information: {response.status_code}")

@app.route('/')
def checkout():
    returnedObj ="amount is"
    return render_template('checkout.html', key="pk_test_51OoQM4Db6e0xe0n3BuJCa1Mt8BUPJCweoQztG5RnKJ4RulsyhNRmQGMB97P4Vvet19yV8DrL4XgcjiWxSLGUqYp400zi3CccES",returnedObj=information['age'])

stripe.api_key = "sk_test_51OoQM4Db6e0xe0n3x00YdJ2FapLr7NZ9XTms5vOb6z64T38InsHjHOjaguKcESoNPCZZ0R225k4PU08aRQFteyA200kQwXA8r3"

@app.route('/charge', methods=['POST'])
def charge():
    website = ''
    json_response = ''
    # Amount in cents
    amount=int(information['age']) * 100 
    try:
        
        

        # Creating a customer
        customer = stripe.Customer.create(
            email='customer@example.com',
            source=request.form['stripeToken']
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Flask Charge'
        )

# 
        # Send reponse to this actual file
        # "/bookings/<int:booking_id>/success"

        # Placeholder
        response = requests.post(
            'http://127.0.0.1:5004/receive_transaction_id',  # Replace with receiver app URL
            json={'transaction_id': charge.id}
        )
        message = 'L'
        if response.status_code == 200:
            message = amount
        return render_template("charge.html",json_response=message)

    except stripe.error.StripeError as e:
        # Attempt to extract transaction value
        transaction_value = getattr(e, 'amount', None) or getattr(e, 'charge', {}).get('amount')

        # Pass error message and extracted transaction value (if available) to the failure template
        jsonify({"error":"Something went wrong"}), 403

        return render_template("failure.html", error_message="Something went wrong with the payment.")

        

if __name__ == '__main__':
    app.run(debug=True, port=4242)