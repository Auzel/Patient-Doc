from flask import Blueprint, request, redirect, render_template, flash, url_for
#from flask_jwt import jwt_required, current_identity
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from models import db, Med_Institution, User, Physician, Patient, Appointment, Med_Record, Release_Form
from werkzeug.security import generate_password_hash, check_password_hash

import datetime
## consider when doctor or patient deleted, is it deleted from other tables
## do routes for ? queries
## account for status codes

##remember to configure flash cards



api = Blueprint('api', __name__)


@api.route('/')
def index():
    if current_user.is_authenticated:
        user=current_user
    return render_template('/front_layout/home.html', user=user) 

@api.route('/signup', methods=['GET', 'POST'])
def signup():
    ### Need to make slight change for physician
    if request.method == 'POST':     
        data=request.form
        DOB = datetime.datetime.strptime(data['DOB'],"%Y-%m-%d")
        type = data['type']
        if type=='patient':
            user = Patient(fname = data['fname'], lname=data['lname'], username=data['uname'], date_of_birth=DOB, 
                      address=data['address'], email=data['email']) # create user object
            user.set_password(data['password']) # set password
        elif type=='physician':
            user = Patient(fname = data['fname'], lname=data['lname'], username=data['uname'], date_of_birth=DOB, 
                        address=data['address'], email=data['email']) ## add other physician fields
        else:
            print('error')                        

        try:
            db.session.add(user) # save new user
            db.session.commit()
        except IntegrityError as e : # attempted to insert a duplicate user
            print('problem: ',e)
            db.session.rollback()
            flash('username or email already exists')
            return redirect(url_for('.signup'))
        flash('Account Created!')
        return render_template('/front_layout/login.html')        
    return render_template('/front_layout/signup.html')


@api.route('/login', methods=['GET', 'POST'])
def login():
    ##when logged in he is redirected to the user-specific page where he can now view his profile/latest medical report or medical reports
    if request.method == 'POST':
        data = request.form
        user = User.query.get(data['username'])

        if user and user.check_password(data['password']):
            login_user(user)
            flash('Logged in successfully.') 
            return redirect(url_for('.index'))
        flash('Invalid username or password') # send message to next page 
    return render_template('/front_layout/login.html')

@api.route('/logout')
@login_required
def logout():
    logout_user(current_user)
    redirect(url_for('.index'))


#NOTE to Shaquille - username is used to refer to patient username and uname is used to refer to physician username

@api.route('/patients/<username>')
@api.route('/physicians/<uname>/patients/<username>')
@login_required
def get_patient(username,uname):

    if (current_user.username==username and current_user.type=='patient'):
        patient=Patient.query.get(username)
    elif current_user.username==uname and current_user.type=='physician':
        appointment=Appointment.query.filter(physician_username=uname, patient_username=username).first()
        if appointment:
            patient=appointment.patient
    return render_template('/users_layout/profile.html', user=patient)


@api.route('/patients/<username>/medical_record')
@api.route('/physicians/<uname>/patients/<username>/medical_record')
@login_required
def get_medical_record(username,uname):

    if current_user.username==username and current_user.type=='patient':
        patient=Patient.query.get(username)
    elif current_user.username==uname and current_user.type=='physician':
        appointment=Appointment.query.filter(physician_username=uname, patient_username=username).first()
        if appointment:
            med_record = appointment.patient.med_record        
    return render_template('/users_layout/medical_record.html',med_record=med_record, username=username)  # do logic and check if med_records


@api.route('/patients/<username>/appointment/<date>')
@api.route('/physicians/<uname>/patients/<username>/appointment/<date>')
@login_required
def get_appointment(username,uname,date):
    date = datetime.datetime.strptime(date,"%d-%m-%Y")
    if (current_user.username==username and current_user.type=='patient') or (current_user.username==uname and current_user.type=='physician'):
        appointment=Appointment.query.filter_by(physician_username=uname, patient_username=username,date=date).first()

    return render_template('/users_layout/appointment.html',appointment=appointment)

@api.route('/patients/<username>/appointments>')
@login_required
def get_patient_appointments(username):
    if current_user.username==username and current_user.type=='patient':
        appointments = Patient.get(username).appointments
    return render_template('/users_layout/appointment_list.html',appointment=appointments)


@api.route('/physicians/<uname>/appointments')
@login_required
def get_physician_appointment(uname):
    if current_user.username==uname and current_user.type=='physician':
        appointments = Physician.get(uname).appointments
    return render_template('/users_layout/appointment_list.html',appointment=appointments)


@api.route('/patients/<username>/physicians')
@login_required
def get_patient_physicians(username):
    physicians=[]
    used=set()
    if current_user.username==username and current_user.type=='patient':
        appointments = Patient.get(username).appointments
        for appointment in appointments:
            if not appointment.physician_username in used:
                used.add(appointment.physician_username)
                physicians.append(appointment.physician)
    return render_template('/users_layout/users_list.html',users=physicians) 


@api.route('/physicians')
def get_physicians():
    physicians=Physician.query.all()
    return render_template('/users_layout/users_list.html',users=physicians)

@api.route('/physicians/<uname>')
def get_physician(uname):    
    physician = Physician.query.filter_by(username = uname).first()
    return render_template('/users_layout/profile.html', user=physician)

@api.route('/physicians/<uname>/patients')
@login_required
def get_physician_patients(uname):
    patients=[]
    used=set()
    if current_user.username==uname and current_user.type=='physician':
        appointments = Physician.get(uname).appointments
        for appointment in appointments:
            if not appointment.patient_username in used:
                used.add(appointment.patient_username)
                patients.append(appointment.patient)
    return render_template('/users_layout/users_list.html',users=patients)

@api.route('/med_instutitions')
def get_med_institutions():
    med_institutions = Med_Institution.query.all()
    return render_template('/users_layout/med_institution_list.html',med_institutions=med_institutions)

@api.route('/med_instutitions/<id>')
def get_med_institutions(id):
    med_institution = Med_Institution.query.get(id)
    return render_template('/users_layout/med_institution.html',med_institution=med_institution)

@api.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404

