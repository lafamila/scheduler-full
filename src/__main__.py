from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/daily')
def _index():
    return render_template('index.html')

@app.route('/week')
def _week():
    return render_template('week.html')

@app.route('/month')
def _month():
    return render_template('month.html')

@app.route('/year')
def _year():
    return render_template('year.html')


if __name__=="__main__":
    app.run(port=20023, debug=True)