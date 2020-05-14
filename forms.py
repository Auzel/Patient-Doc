from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, SelectField, FileField
from wtforms.validators import InputRequired, DataRequired, EqualTo, Email
from wtforms.fields.html5 import  DateField, DateTimeField, TimeField
from wtforms.validators import ValidationError
import datetime
import io

class Login(FlaskForm):
    email= StringField('Email',render_kw={"placeholder": "Email"}, validators=[InputRequired("Please enter your email."), validators.Length(max=50), Email()])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[InputRequired("Please enter your password")])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class SignUp(FlaskForm):    
    name = StringField('Name', validators=[InputRequired("Please enter your first name."), validators.Length(max=41)])
    email= StringField('Email', validators=[InputRequired("Please enter your email."), validators.Length(max=50), Email()])
    password = PasswordField('Password', render_kw={"placeholder": "Atleast 7 characters"}, validators=[InputRequired("Please enter your password."), 
                validators.Length(min=7, max=20,message="Password must be between 7 to 20 characters."), EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired("Please re-enter your password.")] )
    DOB = DateField('Date of Birth', format='%Y-%m-%d',validators=[DataRequired("Please enter your date of birth.")])
    address = StringField('Address', validators=[InputRequired("Please enter your address."), validators.Length(max=50)])
    type = SelectField('User Type', choices=[('patient', 'Patient'), ('physician', 'Physician')] )
    submit = SubmitField('Sign Up')
    
    def validate_DOB(form, field):
        if field.data > datetime.datetime.now().date() - datetime.timedelta(days=18*365):
            raise ValidationError("User must be older than 18 years older")
          

    
class Physician_SignUp(FlaskForm):
    physician_type= SelectField('Physician Type', choices=[('doctor', 'Doctor'), ('dentist', 'Dentist')] )
    degree=StringField('Degree', validators=[InputRequired("Please enter your degree."), validators.Length(max=20)])
    place_of_education=StringField('University', validators=[InputRequired("Please enter the institution where you received your degree."), validators.Length(max=20)])
    license= FileField('License File' ,validators=[DataRequired("Please upload your license file.")] )
    med_key = StringField('Medical Institution Key', validators=[InputRequired("Please enter the key provided by your medical instutitions.")] )

    def validate_license(form, field):
        filename=field.data.filename
        valid = '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg','jpeg','png'}
        if not valid:
            raise ValidationError("Incorrect format")


class Booking(FlaskForm):
    date=DateField('Date', format='%Y-%m-%d', default=datetime.datetime.now().date(), validators=[InputRequired("Please enter the new appointment date.")])
    time=TimeField('Time', validators=[DataRequired("Please enter the new appointment time.")])
    physician_name = StringField("Physician's Name", validators=[InputRequired("Please enter the name of your physician.")])

    def validate_time(form, field):
        timeformat = "%H:%M"
        try:
            validtime = datetime.datetime.strptime(field.data, timeformat)
        except ValueError:
            raise ValidationError("Invalid time chosen.")

    def validate_date(form, field):
        if field.data < datetime.datetime.now():
            raise ValidationError("Cannot set an appointment to before today's date")





