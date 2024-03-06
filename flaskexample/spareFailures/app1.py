from flask import Flask, render_template, request, jsonify
import stripe

app = Flask(__name__)

@app.route('/')
def checkout():
    return render_template('checkout.html', key="pk_test_51OoQM4Db6e0xe0n3BuJCa1Mt8BUPJCweoQztG5RnKJ4RulsyhNRmQGMB97P4Vvet19yV8DrL4XgcjiWxSLGUqYp400zi3CccES")

stripe.api_key = "sk_test_51OoQM4Db6e0xe0n3x00YdJ2FapLr7NZ9XTms5vOb6z64T38InsHjHOjaguKcESoNPCZZ0R225k4PU08aRQFteyA200kQwXA8r3"

@app.route('/charge', methods=['POST'])
def charge():
    website=''
    json_response=''
    try:
        # Amount in cents
        amount = 1000
        # Creating a charge

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


        # Read the JSON response
        json_response =charge
        website='charge.html'
        # Pass the JSON response to the template or handle it as needed

        
    except stripe.error.CardError as e:
        # Handle card errors
        json_response =charge
        json_response =e
        json_response= jsonify({'error': e}), 403
        website='failure.html'
        return render_template('failure.html',error =str(e))
    # ... Handle other exceptions ...
        

    return render_template(website,json_response=json_response)

if __name__ == '__main__':
    app.run(debug=True)

   