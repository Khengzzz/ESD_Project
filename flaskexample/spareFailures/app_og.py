from flask import Flask, render_template,request
import stripe
app = Flask(__name__)

@app.route('/')
def checkout():
    return render_template('checkout.html',key="pk_test_51OoQM4Db6e0xe0n3BuJCa1Mt8BUPJCweoQztG5RnKJ4RulsyhNRmQGMB97P4Vvet19yV8DrL4XgcjiWxSLGUqYp400zi3CccES")

stripe.api_key = "sk_test_51OoQM4Db6e0xe0n3x00YdJ2FapLr7NZ9XTms5vOb6z64T38InsHjHOjaguKcESoNPCZZ0R225k4PU08aRQFteyA200kQwXA8r3"

@app.route('/charge', methods=['POST'])
def charge():
        # Amount in cents
    amount = 1000

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
   
    return render_template('charge.html', amount=amount)

if __name__ == '__main__':
    app.run()