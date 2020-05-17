from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, SelectField, FileField, TextAreaField, IntegerField
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
    DOB = DateField('Date of Birth',render_kw={"placeholder": "dd/mm/yyyy"}, format='%Y-%m-%d',validators=[InputRequired("Please enter your date of birth.")])
    address = StringField('Address', validators=[InputRequired("Please enter your address."), validators.Length(max=50)])
    type = SelectField('User Type', choices=[('patient', 'Patient'), ('physician', 'Physician')] )
    user_img= FileField('Profile Photo' ,validators=[DataRequired("Please upload a photo of yourself.")] )
    submit = SubmitField('Sign Up')
    
    def validate_DOB(form, field):
        if field.data > datetime.datetime.now().date() - datetime.timedelta(days=18*365):
            raise ValidationError("User must be older than 18 years older")

    def validate_user_img(form, field):
        filename=field.data.filename
        valid = '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg','jpeg','png'}
        if not valid:
            raise ValidationError("Incorrect format") 

    
class Physician_SignUp(FlaskForm):
    physician_type= SelectField('Physician Type', choices=[('doctor', 'Doctor'), ('dentist', 'Dentist')] )
    degree=StringField('Degree', validators=[InputRequired("Please enter your degree."), validators.Length(max=20)])
    place_of_education=StringField('University', validators=[InputRequired("Please enter the institution where you received your degree."), validators.Length(max=20)])
    #license= FileField('License File' ,validators=[DataRequired("Please upload your license file.")] )
    med_key = StringField('Medical Institution Key', validators=[InputRequired("Please enter the med ID assigned to your medical instutitions.")])

    '''
    def validate_license(form, field):
        filename=field.data.filename
        valid = '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg','jpeg','png'}
        if not valid:
            raise ValidationError("Incorrect format")
    '''

class Booking(FlaskForm):
    date=DateField('Date', format='%Y-%m-%d',render_kw={"placeholder": "dd/mm/yyyy"}, default=datetime.datetime.now().date(), validators=[InputRequired("Please enter the new appointment date.")])
    time=TimeField('Time', render_kw={"placeholder": "HH:MM"}, validators=[InputRequired("Please enter the new appointment time.")])
    physician_email = StringField("Physician's Email", validators=[InputRequired("Please enter the email of your physician."), validators.Length(max=50), Email()])

    def validate_time(form, field):
        timeformat = "%H:%M"
        try:
            validtime = datetime.datetime.strptime((str(field.data))[:5], timeformat)      #come back and only allow selection every half hour
        except ValueError:
            print("here")
            raise ValidationError("Invalid time chosen.")

    def validate_date(form, field):
        if field.data < datetime.datetime.now().date():
            print("here2")
            raise ValidationError("Cannot set an appointment to before today's date")


class Med_Record_SetUp(FlaskForm):
    current_problem = StringField('Current Problem', validators=[InputRequired("Please enter your current problem."), validators.Length(max=50)])
    current_treatment=StringField('Current Treatment', default ="None", validators=[validators.Length(max=50)])
    history=TextAreaField('Medicial History',render_kw={'rows':'8'}, validators=[InputRequired("Please enter your medical history. If none, state 'None'."), validators.Length(max=2000)])

class Med_Record_Problem(FlaskForm):
    current_problem = StringField('Current Problem', validators=[InputRequired("Please enter your current problem."), validators.Length(max=50)])

class Med_Record_Treatment(FlaskForm):
    current_treatment=StringField('Current Treatment', validators=[InputRequired("Please enter the current treatment."), validators.Length(max=50)])






