from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, SelectField, FileField
from wtforms.validators import InputRequired, DataRequired, EqualTo, Email
from wtforms.fields.html5 import  DateField
from wtforms.validators import ValidationError
import re

class Login(FlaskForm):
    email= StringField('Email',render_kw={"placeholder": "Email"}, validators=[InputRequired("Please enter your email."), validators.Length(max=50), Email()])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[InputRequired("Please enter your password")])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class SignUp(FlaskForm):    
    name = StringField('Name', render_kw={"placeholder": "John Doe"},validators=[InputRequired("Please enter your first name."), validators.Length(max=41)])
    email= StringField('Email', validators=[InputRequired("Please enter your email."), validators.Length(max=50), Email()])
    password = PasswordField('Password', render_kw={"placeholder": "Atleast 7 characters"}, validators=[InputRequired("Please enter your password."), 
                validators.Length(min=7, max=20,message="Password must be between 7 to 20 characters."), EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired("Please re-enter your password.")] )
    DOB = DateField('Date of Birth', format='%Y-%m-%d',  validators=[InputRequired("Please enter your date of birth.")])
    address = StringField('Address', validators=[InputRequired("Please enter your address."), validators.Length(max=50)])
    type = SelectField('User Type', choices=[('patient', 'Patient'), ('physician', 'Physician')] )
    submit = SubmitField('Sign Up')
    physician_type= SelectField('Physician Type', choices=[('doctor', 'Doctor'), ('dentist', 'Dentist')] )
    degree=StringField('Degree', validators=[InputRequired("Please enter your degree."), validators.Length(max=20)])
    place_of_education=StringField('University', validators=[InputRequired("Please enter the institution where you received your degree."), validators.Length(max=20)])
    license= FileField('License File' ,validators=[DataRequired("Please upload your license file.")] )
    med_key = StringField('Medical Institution Key', validators=[InputRequired("Please enter the key provided by your medical instutitions.")] )
    
    def validate_license(form, field):
        print("here")
        filename=field.data.read().decode('UTF-8')
        valid = '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg','jpeg','png'}
        print("Philmon",filename)
        if not valid:
            raise ValidationError("Incorrect format")
        
        

    '''
    def validate_license(form, field):
        if field.data:
            field.data = re.sub(r'[^a-z0-9_.-]', '_', field.data)
    '''

class Physician_Profile(SignUp):
    
    type= SelectField('Physician Type', choices=[('doctor', 'Doctor'), ('dentist', 'Dentist')] )
    degree=StringField('Degree', validators=[InputRequired("Please enter your degree."), validators.Length(max=20)])
    place_of_education=StringField('Education Institution', validators=[InputRequired("Please enter the institutioon where you received your degree."), validators.Length(max=20)])
    med_id=SelectField('Medical Institution', choices=[('patient', 'Patient'), ('physician', 'Physician')] )
    DOB = DateField('Date', validators=[InputRequired("Please enter your date of birth.")])
    address = StringField('Address', validators=[InputRequired("Please enter your address."), validators.Length(max=50)])


class Patient_Profile(SignUp):

    DOB = DateField('Date', validators=[InputRequired("Please enter your date of birth.")])
    address = StringField('Address', validators=[InputRequired("Please enter your address."), validators.Length(max=50)])

