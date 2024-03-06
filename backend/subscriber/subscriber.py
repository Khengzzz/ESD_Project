from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/subscription'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Subscription(db.Model):
    __tablename__ = 'subscription'


    screening_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    notification_status = db.Column(db.Enum('Pending', 'Notified'), nullable=False, default='Pending')
    creation_timestamp = db.Column(db.TIMESTAMP, default=datetime.utcnow)


    def __init__(self, screening_id, user_id, notification_status, creation_timestamp):
        self.screening_id = screening_id
        self.user_id = user_id
        self.notification_status = notification_status
        self.creation_timestamp = creation_timestamp


    def json(self):
        return {
            "screening_id": self.screening_id, 
            "user_id": self.user_id, 
            "notification_status": self.notification_status, 
            "creation_timestamp": self.creation_timestamp.isoformat()
        }


@app.route("/subscriptions/<string:screening_id>")
def get_subscribers_by_screening(screening_id):
    subscriber_list = Subscription.query.filter_by(screening_id=screening_id).all()

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
            "message": f"There are no subscribers for the event."
        }), 404

@app.route("/subscribe", methods=['POST'])
def subscribe_user():
    screening_id = request.args.get("screening_id")
    user_id = request.args.get("user_id")
    if (db.session.scalars(
      db.select(Subscription).filter_by(screening_id=screening_id, user_id=user_id).
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
                "message": "User already subscribed to the event."
            }
        ), 400


    data = request.get_json()
    user_subscription = Subscription(screening_id, user_id, **data)


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

@app.route("/unsubscribe", methods=['DELETE'])
def unsubscribe_user():
    screening_id = request.args.get("screening_id")
    user_id = request.args.get("user_id")

    existing_subscription = db.session.scalars(
        db.select(Subscription).filter_by(screening_id=screening_id, user_id=user_id).limit(1)
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
                    "message": "User successfully unsubscribed from the event."
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
                "message": "Subscription does not exist."
            }
        ), 400
    
if __name__ == '__main__':
    app.run(port=5000, debug=True)