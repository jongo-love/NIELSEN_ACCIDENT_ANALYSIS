# LINE 1-10 I'M CREATING ROUTES FOR THE HOME PAGE.
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/home')
def HOME():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)