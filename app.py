# LINE 1-10 I'M CREATING ROUTES FOR THE HOME PAGE.
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nielsenaccident.db'  # SQLite database file path
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

#with app.app_context():
    #db.create_all()
    #db.session.commit()



@app.route('/home')
def HOME():
    return render_template('home.html')

@app.route('/about')
def ABOUT():
    return render_template('about.html')

@app.route('/contact')
def CONTACT():
    return render_template('contact.html')




if __name__ == '__main__':
    app.run(debug=True)