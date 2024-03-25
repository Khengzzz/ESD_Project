from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from os import environ
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/subscriber'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Subscriber db and table
class Subscriber(db.Model):
    __tablename__ = 'subscriber'

    screening_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), nullable=False)


    def __init__(self, screening_id, user_id, user_email):
        self.screening_id = screening_id
        self.user_id = user_id
        self.user_email = user_email


    def json(self):
        return {
            "screening_id": self.screening_id, 
            "user_id": self.user_id,
            "user_email": self.user_email
        }


# Route handler to retrieve all subscribers for a specific screening based on 'screening_id'
@app.route("/subscribers/subscriptions/<string:screening_id>")
def get_subscribers_by_screening(screening_id):
    subscriber_list = Subscriber.query.filter_by(screening_id=screening_id).all()

    if subscriber_list:
        return jsonify({
            "code": 200,
            "data": {
                "subscribers": [subscriber.json() for subscriber in subscriber_list]
            }
        }), 200
    else:
        return jsonify({
            "code": 404,
            "message": f"There are no subscribers for the movie screening."
        }), 404


# Route handler to subscribe a user to a screening
@app.route("/subscribers/subscribe", methods=['POST'])
def subscribe_user():
    screening_id = request.args.get("screening_id")
    user_id = request.args.get("user_id")
    email = request.args.get("email")
    if (db.session.scalars(
        db.select(Subscriber).filter_by(screening_id=screening_id, user_id=user_id).
        limit(1)
        ).first()
        ):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "screening_id": screening_id,
                    "user_id": user_id
                },
                "message": "User already subscribed to the movie screening."
            }
        ), 400



    user_subscription = Subscriber(screening_id, user_id, email)

    try:
        db.session.add(user_subscription)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "screening_id": screening_id,
                    "user_id": user_id
                },
                "message": "An error occurred in subscribing the user."
            }
        ), 500


    return jsonify(
        {
            "code": 201,
            "data": user_subscription.json()
        }
    ), 201


# Route handler to unsubscribe a user from a screening
@app.route("/subscribers/unsubscribe", methods=['DELETE'])
def unsubscribe_user():
    screening_id = request.args.get("screening_id")
    user_id = request.args.get("user_id")

    existing_subscription = db.session.scalars(
        db.select(Subscriber).filter_by(screening_id=screening_id, user_id=user_id).limit(1)
    ).first()

    if existing_subscription:
        try:
            db.session.delete(existing_subscription)
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "screening_id": screening_id,
                        "user_id": user_id
                    },
                    "message": "User successfully unsubscribed from the movie screening."
                }
            ), 200
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "screening_id": screening_id,
                        "user_id": user_id
                    },
                    "message": f"An error occurred in unsubscribing the user: {str(e)}"
                }
            ), 500
    else:
        return jsonify(
            {
                "code": 400,
                "data": {
                    "screening_id": screening_id,
                    "user_id": user_id
                },
                "message": "Subscriber does not exist."
            }
        ), 400
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)