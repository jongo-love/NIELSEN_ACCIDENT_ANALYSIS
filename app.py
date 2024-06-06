# LINE 1-10 I'M CREATING ROUTES FOR THE HOME PAGE.
import time
from flask_mail import Message,Mail
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired,EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

#IMPORTING LIBRARIES THAT WILL BE USED IN DATA SCIENCE.
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns  
from matplotlib import cm  
import matplotlib
import matplotlib.patches as mpatches
import geopandas as gpd
from geopy.geocoders import Nominatim
from shapely.geometry import Point

app = Flask(__name__)
login_manager = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nielsenaccident.db'  # SQLite database file path
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jongolove01@gmail.com'
app.config['MAIL_PASSWORD'] = 'ctsy mhos lokr jzdn'
app.config['MAIL_DEFAULT_SENDER'] = 'jongolove01@gmail.com'
db = SQLAlchemy(app)
mail = Mail(app)

# Define the User model/ Creating the USER table in the database.
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True,)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Register')

class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

# Configure Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#with app.app_context():
    #db.create_all()
    #db.session.commit()

@app.route('/home')
@login_required
def HOME():
    return render_template('home.html')

@app.route('/about')
@login_required
def ABOUT():
    return render_template('about.html')

@app.route('/contact',methods=['GET', 'POST'])
@login_required
def CONTACT():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Compose the email message
        sender = app.config['MAIL_DEFAULT_SENDER']  # Assigning the sender
        msg = Message(subject='New Contact Form Submission',
                    sender=sender,
                    recipients=['jongolove01@gmail.com'])
        msg.body = f'Name: {name}\nEmail: {email}\nMessage: {message}'

        # Send the email
        mail.send(msg)

        # Redirect to a thank you page or home page after successful submission
        return redirect(url_for('THANKYOU'))
    return render_template('contact.html')

@app.route('/thank_you')
@login_required
def THANKYOU():
    return render_template('thanks.html')

@app.route('/', methods=['GET', 'POST'])
def LOGIN():
    time.sleep(1.5)
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        # You can handle the form data here
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password)and user.email == email:
                login_user(user)
                flash('Logged in successfully.')
                return redirect(url_for('HOME'))
            else:
                error = 'Incorrect password. Please try again.'
        else:
            error = 'Username not found. Please register.'
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
@login_required
def LOGOUT():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('LOGIN'))

@app.route('/register', methods=['GET', 'POST']) 
def REGISTER():
    time.sleep(1.5)
    form = RegistrationForm()
    error = None
    if form.validate_on_submit():
        # You can handle the form data here
        username = form.username.data
        password = form.password.data
        email = form.email.data
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            error = 'Username already exists. Please choose a different one.'
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password,email=email)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('LOGIN'))
    
    return render_template('register.html', form=form, error=error)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a password reset token
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = serializer.dumps(user.email, salt='password-reset-salt')
            # Send password reset email with the token
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Password Reset', recipients=[user.email])
            msg.body = f'Click the following link to reset your password: {reset_url}'
            mail.send(msg)  # Send the email
            flash('Password reset email sent. Please check your email.')
            return redirect(url_for('LOGIN'))
        else:
            flash('Email address not found. Please try again.')
    return render_template('forgot_password.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
@login_required
def reset_password(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # Token expires after 1 hour
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Invalid or expired token. Please try again.')
            return redirect(url_for('forgot_password'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            # Update user's password
            hashed_password = generate_password_hash(form.password.data)
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been reset. You can now log in with your new password.')
            return redirect(url_for('LOGIN'))
        return render_template('reset_password.html', form=form)
    except Exception as e:
        print(e)
        flash('Invalid or expired token. Please try again.')
        return redirect(url_for('forgot_password'))

#the function of this route is, when the Data Analysis and Visualization service is clicked, the page should return a beautiful
# dashboard which WILL have buttons for the different kind of visualizations.
#@app.route('/data_analysis')
#def DASHBOARD():
    #return render_template('dashboard.html')


@app.route('/data_analysis')
@login_required
def DATALYSIS():
    conn = sqlite3.connect('C:\\Users\\students\\NIELSEN_ACCIDENT_ANALYSIS\\instance\\nielsenaccident.db')
    df = pd.read_sql_query("SELECT * FROM accidents", conn)
    conn.close()
    
    df['Start_Time'] = pd.to_datetime(df['Start_Time'])
    df['End_Time'] = pd.to_datetime(df['End_Time'])
    
    city_accidents = df['City'].value_counts().reset_index()
    city_accidents.columns = ['City', 'Accident Cases']
    
    top_8_cities = city_accidents.head(8)
    
    # Customized visualization
    fig, ax = plt.subplots(figsize=(12, 7), dpi=80)
    cmap = cm.get_cmap('rainbow', 8)
    clrs = [cm.colors.rgb2hex(cmap(i)) for i in range(cmap.N)]
    
    ax = sns.barplot(y=top_8_cities['Accident Cases'], x=top_8_cities['City'], palette=clrs)
    
    total = sum(city_accidents['Accident Cases'])
    for i in ax.patches:
        ax.text(i.get_x() + 0.03, i.get_height() - 2500,
                f"{round((i.get_height()/total)*100, 2)}%", fontsize=15, weight='bold', color='white')
    
    plt.title('Top 10 Cities in US with the Most Number of Road Accident Cases (2016-2020)',
              size=20, color='grey')
    plt.ylim(0, 50000)
    plt.xticks(rotation=10, fontsize=12)
    plt.yticks(fontsize=12)
    
    ax.set_xlabel('\nCities\n', fontsize=15, color='grey')
    ax.set_ylabel('Accident Cases\n', fontsize=15, color='grey')
    
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('white')
        ax.spines[spine].set_linewidth(1.5)
    
    right_side = ax.spines['right']
    right_side.set_visible(False)
    top_side = ax.spines['top']
    top_side.set_visible(False)
    
    ax.set_axisbelow(True)
    ax.grid(color='#b2d6c7', linewidth=1, axis='y', alpha=0.3)
    
    MA = mpatches.Patch(color=clrs[0], label='City with Maximum\n no. of Road Accidents')
    ax.legend(handles=[MA], prop={'size': 10.5}, loc='best', borderpad=1, 
              labelcolor=clrs[0], edgecolor='white')

    custom_plot_path = 'static/custom_plot.png'
    plt.savefig(custom_plot_path)
    plt.close()

    # Pass the data and paths to the template
    return render_template('datalysis.html', plot_path=custom_plot_path)


#INCLUDE THE DATABASE IMPLEMENTATION FOR THE CODE PRESUME FUNCTIONALITY.

@app.route('/accident_investigation')
@login_required
def ACCIDENT_INVESTIGATION():
    return render_template('accident_investigation.html')

@app.route('/safety_audit_assessment')
@login_required
def SAFETYAUDITS_ASSESSMENTS():
    return render_template('safety_audit_assessment.html')

@app.route('/research_development')
@login_required
def RESEARCH_DEVELOPMENT():
    return render_template('research_development.html')

@app.route('/custom_solution_software')
@login_required
def CUSTOM_SOLUTION_SOFTWARE():
    return render_template('custom_solution_software.html')

@app.route('/safety_equipment')
@login_required
def SAFETY_EQUIPMENT():
    return render_template('safety_equipment.html')


@app.route('/events_calendar')
@login_required
def EVENTS():
    return render_template('events_calendar.html')

@app.route('/community_guidlines')
@login_required
def COMMUNITY_GUIDLINES():
    return render_template('community_guidlines.html')

if __name__ == '__main__':
    app.run(debug=True, port=3672)
