from flask_cors import CORS
from flask import Flask, render_template
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/screening')
def screening():
    return render_template('screening.html')

@app.route('/mypurchase')
def mypurchase():
    return render_template('my_purchase.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1234, debug=False)