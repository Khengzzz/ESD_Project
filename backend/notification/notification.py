from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/notifications'
db = SQLAlchemy(app)

class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    notification_content = db.Column(db.Text, nullable=False)
    delivery_status = db.Column(db.Enum('Pending', 'Notified'), nullable=False, default='Pending')
    creation_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, user_id, notification_content, delivery_status='Pending'):
        self.user_id = user_id
        self.notification_content = notification_content
        self.delivery_status = delivery_status

    def json(self):
        return {
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "notification_content": self.notification_content,
            "delivery_status": self.delivery_status,
            "creation_timestamp": self.creation_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }


@app.route('/notifications/<int:notification_id>', methods=['GET'])
def get_notification(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({'message': 'Notification not found'}), 404
    return jsonify({
        'id': notification.id,
        'user_id': notification.user_id,
        'notification_content': notification.notification_content,
        'delivery_status': notification.delivery_status,
        'creation_timestamp': notification.creation_timestamp
    })

@app.route('/notifications/<int:notification_id>', methods=['PUT'])
def update_notification(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({'message': 'Notification not found'}), 404
    
    data = request.json
    notification.delivery_status = data.get('delivery_status', notification.delivery_status)
    db.session.commit()
    
    return jsonify({'message': 'Notification updated successfully'})

@app.route('/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({'message': 'Notification not found'}), 404
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'message': 'Notification deleted successfully'})

@app.route('/notifications/send', methods=['POST'])
def send_notification():
    data = request.json
    user_id = data.get('user_id')
    notification_content = data.get('notification_content')
    
    if not all([user_id, notification_content]):
        return jsonify({'message': 'Missing required data'}), 400
    
    notification = Notification(user_id=user_id, notification_content=notification_content)
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'message': 'Notification sent successfully'}), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
