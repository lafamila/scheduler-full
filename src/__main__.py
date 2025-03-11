from flask import Flask, render_template, request
from api import bp
app = Flask(__name__)
app.register_blueprint(bp)
@app.route('/')
@app.route('/daily')
def _index():
    target_date = request.args.get("target_date", None)
    return render_template('index.html', target_date=target_date)

@app.route('/week')
def _week():
    return render_template('week.html')

@app.route('/month')
def _month():
    target_month = request.args.get("target_month", None)
    return render_template('month.html', target_month=target_month)

@app.route('/year')
def _year():
    return render_template('year.html')


if __name__=="__main__":
    app.run(port=20023, debug=True)