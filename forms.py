from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators
from wtforms.validators import InputRequired, EqualTo, Email

class Login(FlaskForm):
    username = StringField('Username', render_kw={"placeholder": "Username"},validators=[InputRequired(), validators.Length(max=20)])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[InputRequired(), validators.Length(max=20)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class Sign_Up_Patient(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    email = StringField('email', validators=[Email(), InputRequired()])
    password = PasswordField('New Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    submit = SubmitField('Sign Up', render_kw={'class': 'btn waves-effect waves-light white-text'})

class Sign_Up_Physician(Sign_Up_Patient):
    username = StringField('username', validators=[InputRequired()])
    email = StringField('email', validators=[Email(), InputRequired()])
    password = PasswordField('New Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    submit = SubmitField('Sign Up', render_kw={'class': 'btn waves-effect waves-light white-text'})
'''
username=db.Column(db.String(20), nullable=False, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    password=db.Column(db.String(80), nullable=False)
    date_of_birth=db.Column(db.Date, nullable=False)
    address=db.Column(db.String(50), nullable=False)
    email= db.Column(db.String(50), nullable=False, unique=True)
'''