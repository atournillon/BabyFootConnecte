from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/livematch')
def live_match():
    return render_template('livematch.html')

if __name__ == '__main__':
    app.run(debug=True)
