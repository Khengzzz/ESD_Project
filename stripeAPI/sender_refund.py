from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/refundNo.')
def send_data():
    # Replace with your logic to generate the data
    data = {'booking_id':4}
    
    # Convert data to JSON
    response = jsonify(data)
    return response



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":

    app.run(port=5200, debug=True)
