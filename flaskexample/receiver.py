from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive_transaction_id', methods=["POST"])
def receive_transaction_id():
    try:
        # Retrieve the transaction ID from the request
        data = request.get_json()
        transaction_id = data['transaction_id']
        print(transaction_id)
        # Replace with your logic for handling the transaction ID (e.g., store it in a database)
        # **DO NOT** process payments or store sensitive information in this app.

        return jsonify({'message': f'Received transaction ID: {transaction_id}'})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True,port=5004)
