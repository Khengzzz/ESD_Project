from flask_cors import CORS
from flask import Flask, render_template,url_for
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)

app.static_folder = 'static' 
@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/screening/<screening_id>')
def screening(screening_id):
    return render_template('screening.html',screening_id=screening_id)

@app.route('/mypurchase')
def mypurchase():
    return render_template('my_purchase.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1234, debug=False)