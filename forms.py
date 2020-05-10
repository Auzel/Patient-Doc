from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, DateField, SelectField
from wtforms.validators import InputRequired, EqualTo, Email

class Login(FlaskForm):
    email= StringField('Email',render_kw={"placeholder": "Email"}, validators=[InputRequired("Please enter your email."), validators.Length(max=50), Email()])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[InputRequired("Please enter your password")])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class SignUp(FlaskForm):    
    name = StringField('Name', render_kw={"placeholder": "John Doe"},validators=[InputRequired("Please enter your first name."), validators.Length(max=41)])
    type = SelectField('User Type', choices=[('patient', 'Patient'), ('physician', 'Physician')], validators= [InputRequired("Please enter your user type.")] )
    email= StringField('Email', validators=[InputRequired("Please enter your email."), validators.Length(max=50), Email()])
    password = PasswordField('Password', render_kw={"placeholder": "Atleast 7 characters"}, validators=[InputRequired("Please enter your password."), 
                validators.Length(min=7, max=20,message="Password must be between 7 to 20 characters."), EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired("Please re-enter your password.")] )
    submit = SubmitField('Sign Up')

class Physician_Profile(FlaskForm):
    #email = StringField('email', validators=[Email(), InputRequired()])
    password = PasswordField('New Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    submit = SubmitField('Sign Up', render_kw={'class': 'btn waves-effect waves-light white-text'})


    DOB = DateField('Date', render_kw={"placeholder": "Date"}, validators=[InputRequired("Please enter your date of birth.")])
    address = StringField('Address', render_kw={"placeholder": "Address"},validators=[InputRequired("Please enter your address."), validators.Length(max=50)])

class Patient_Profile(FlaskForm):
    pass
'''

    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    password=db.Column(db.String(80), nullable=False)
    date_of_birth=db.Column(db.Date, nullable=False)
    address=db.Column(db.String(50), nullable=False)
    email= db.Column(db.String(50), nullable=False, unique=True)
'''