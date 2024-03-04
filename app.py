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
import seaborn as sns  
from matplotlib import cm, patches  
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

@app.route('/data_analysis')
@login_required
def DATALYSIS():
    # Connect to your SQLite database
    # Download DB BROWSER and connect to database.
    conn = sqlite3.connect('C:\\Users\\students\\NIELSEN_ACCIDENT_ANALYSIS\\instance\\nielsenaccident.db')
    cursor = conn.cursor()
    # Execute a query to fetch data from your database
    cursor.execute('SELECT * FROM us_accidents')
    
    # Fetch all rows from the query result
    data = cursor.fetchall()

    # Close the database connection
    conn.close()
    
    #Loading data into the pandas dataframe.
    df = pd.DataFrame(data)
    print('The Dataset Contains, Rows: {:,d} & Columns: {}'.format(df.shape[0], df.shape[1]))
    
    # convert the Start_Time & End_Time Variable into Datetime Feature
    df.Start_Time = pd.to_datetime(df.Start_Time)
    df.End_Time = pd.to_datetime(df.End_Time)
    
    #CITY ANALYSIS
    # create a dataframe of city and their corresponding accident cases
    city_df = pd.DataFrame(df['City'].value_counts()).reset_index().rename(columns={'index':'City', 'City':'Cases'})
    top_20_cities = pd.DataFrame(city_df.head(20))
    
    #visualization: Bar plot of top 20 cities
    fig,ax = plt.subplots(figsize = (12,7), dpi = 80)

    cmap = cm.get_cmap('rainbow', 10)   
    clrs = [matplotlib.colors.rgb2hex(cmap(i)) for i in range(cmap.N)]

    ax=sns.barplot(y=top_20_cities['Cases'], x=top_20_cities['City'], palette='rainbow')

    total = sum(city_df['Cases'])
    for i in ax.patches:
        ax.text(i.get_x()+.03, i.get_height()-2500, \
            str(round((i.get_height()/total)*100, 2))+'%', fontsize=15, weight='bold',
                color='white')

    plt.title('\nTop 10 Cities in US with most no. of \nRoad Accident Cases (2016-2020)\n', size=20, color='grey')

    plt.rcParams['font.family'] = "Microsoft JhengHei UI Light"
    plt.rcParams['font.serif'] = ["Microsoft JhengHei UI Light"]

    plt.ylim(1000, 50000)
    plt.xticks(rotation=10, fontsize=12)
    plt.yticks(fontsize=12)

    ax.set_xlabel('\nCities\n', fontsize=15, color='grey')
    ax.set_ylabel('\nAccident Cases\n', fontsize=15, color='grey')

    for i in ['bottom', 'left']:
        ax.spines[i].set_color('white')
        ax.spines[i].set_linewidth(1.5)
    
    right_side = ax.spines["right"]
    right_side.set_visible(False)
    top_side = ax.spines["top"]
    top_side.set_visible(False)

    ax.set_axisbelow(True)
    ax.grid(color='#b2d6c7', linewidth=1, axis='y', alpha=.3)
    MA = patches.Patch(color=clrs[0], label='City with Maximum\n no. of Road Accidents')
    ax.legend(handles=[MA], prop={'size': 10.5}, loc='best', borderpad=1, 
          labelcolor=clrs[0], edgecolor='white')
    plt.show()
    # Save the plot to a file
    plot_path = 'static/top_20_cities_plot.png'
    plt.savefig(plot_path)
    
    # US States
    states = gpd.read_file('C:\\Users\\STUDENTS\\Downloads\\States_shapefile-shp')

    def lat(city):
        address=city
        geolocator = Nominatim(user_agent="Your_Name")
        location = geolocator.geocode(address)
        return (location.latitude)

    def lng(city):
        address=city
        geolocator = Nominatim(user_agent="Your_Name")
        location = geolocator.geocode(address)
        return (location.longitude)

# list of top 20 cities
    top_twenty_city_list = list(city_df.City.head(20))

    top_twenty_city_lat_dict = {}
    top_twenty_city_lng_dict = {}
    for i in top_twenty_city_list:
        top_twenty_city_lat_dict[i] = lat(i)
        top_twenty_city_lng_dict[i] = lng(i)
    
    top_20_cities_df = df[df['City'].isin(list(top_20_cities.City))]

    top_20_cities_df['New_Start_Lat'] = top_20_cities_df['City'].map(top_twenty_city_lat_dict)
    top_20_cities_df['New_Start_Lng'] = top_20_cities_df['City'].map(top_twenty_city_lng_dict)
    geometry_cities = [Point(xy) for xy in zip(top_20_cities_df['New_Start_Lng'], top_20_cities_df['New_Start_Lat'])]
    geo_df_cities = gpd.GeoDataFrame(top_20_cities_df, geometry=geometry_cities)
    fig,ax = plt.subplots(figsize=(15,15))
    ax.set_xlim([-125,-65])
    ax.set_ylim([22,55])
    states.boundary.plot(ax=ax, color='grey');

    colors = ['#e6194B','#f58231','#ffe119','#bfef45','#3cb44b', '#aaffc3','#42d4f4','#4363d8','#911eb4','#f032e6']
    markersizes = [50+(i*20) for i in range(10)][::-1]
    for i in range(10):
        geo_df_cities[geo_df_cities['City'] == top_twenty_city_list[i]].plot(ax=ax, markersize=markersizes[i], 
                                                                      color=colors[i], marker='o', 
                                                                      label=top_twenty_city_list[i], alpha=0.7)
    
    plt.legend(prop={'size': 13}, loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5), edgecolor='white', title="Cities", title_fontsize=15);

    for i in ['bottom', 'top', 'left', 'right']:
        side = ax.spines[i]
        side.set_visible(False)
    
    plt.tick_params(top=False, bottom=False, left=False, right=False,
                labelleft=False, labelbottom=False)

    plt.title('\nVisualization of Top 10 Accident Prone Cities in US (2016-2020)', size=20, color='grey')
    plt.show()
    # Save the second visualization (the map) to an image file
    map_plot_path = 'static/accident_map_plot.png'
    plt.savefig(map_plot_path)
    
    #TIMEZONE ANALYSIS.
    timezone_df = pd.DataFrame(df['Timezone'].value_counts()).reset_index().rename(columns={'index':'Timezone', 'Timezone':'Cases'})
    fig, ax = plt.subplots(figsize = (10,6), dpi = 80)

    cmap = cm.get_cmap('spring', 4)   
    clrs = [matplotlib.colors.rgb2hex(cmap(i)) for i in range(cmap.N)]

    ax=sns.barplot(y=timezone_df['Cases'], x=timezone_df['Timezone'], palette='spring')

    total = df.shape[0]
    for i in ax.patches:
        ax.text(i.get_x()+0.3, i.get_height()-50000, \
            '{}%'.format(round(i.get_height()*100/total)), fontsize=15,weight='bold',
                color='white')
    
    plt.ylim(-20000, 700000)
    plt.title('\nPercentage of Accident Cases for \ndifferent Timezone in US (2016-2020)\n', size=20, color='grey')
    plt.ylabel('\nAccident Cases\n', fontsize=15, color='grey')
    plt.xlabel('\nTimezones\n', fontsize=15, color='grey')
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=12)
    for i in ['top', 'right']:
        side = ax.spines[i]
        side.set_visible(False)
    
    ax.set_axisbelow(True)
    ax.grid(color='#b2d6c7', linewidth=1, axis='y', alpha=.3)
    ax.spines['bottom'].set_bounds(0.005, 3)
    ax.spines['left'].set_bounds(0, 700000)

    MA = mpatches.Patch(color=clrs[0], label='Timezone with Maximum\n no. of Road Accidents')
    MI = mpatches.Patch(color=clrs[-1], label='Timezone with Minimum\n no. of Road Accidents')
    ax.legend(handles=[MA, MI], prop={'size': 10.5}, loc='best', borderpad=1, 
          labelcolor=[clrs[0], 'grey'], edgecolor='white')
    plt.show()
    # Save the third visualization (Timezone) to an image file
    timezone_plot_path = 'static/timezone_accident_plot.png'
    plt.savefig(timezone_plot_path)
    
    
    
    return render_template('datalysis.html', plot_path=plot_path, map_plot_path=map_plot_path, timezone_plot_path=timezone_plot_path)
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
