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
    
if __name__ == '__main__':
    app.run(debug=True, port=3672)