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
    user=None
    if current_user.is_authenticated:
        if current_user.type == 'patient':
            user=Patient.query.filter_by(username = current_user.username).first()
        elif current_user.type == 'physician':
            user=Physician.query.filter_by(username = current_user.username).first()
        else:        
            print("error")
    
    ## send patient or physician to home page
    return render_template('/front_layout/home.html', user=user) 

@api.route('/signup', methods=['GET', 'POST'])
def signup():
    ### Need to make slight change for physician
    if request.method == 'POST':     
        data=request.form
        DOB = datetime.datetime.strptime(data['DOB'],"%Y-%m-%d")
        patient = Patient(fname = data['fname'], lname=data['lname'], username=data['uname'], date_of_birth=DOB, address=data['address'], email=data['email']) # create user object
        patient.set_password(data['password']) # set password
        try:
            db.session.add(patient) # save new user
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
        user = User.query.filter_by(username = data['username']).first()

        if user and user.check_password(data['password']):
            login_user(user)
            flash('Logged in successfully.') 
            return redirect(url_for('.index'))
        flash('Invalid username or password') # send message to next page 
    return render_template('/front_layout/login.html')


@api.route('/users')
def get_users():
    name="Profile"
    users=None ##change
    return render_template('users_list.html',users=users)

@api.route('/patients')
def get_patients():
    pass##  return render_template('users_list.html',users=users)


@api.route('/patients/<id>')
def get_patient(id):
    #if username in ##users_list/database:
        #users = User[username]
    user=None
    return render_template('/users_layout/profile.html', user=user)
    pass   ##   return render_template('profile.html',user=user)

@api.route('/users_layout/medical_records')
def get_medical_records_from():
    return render_template('/users_layout/medical_records.html', name="Medical")

@api.route('/patients/<id>/medical_records')
def get_medical_records_from_patient(id):
    pass ##return render_template('medical_records.html',medical_records=medical_records)


@api.route('/patients/<id>/medical_records/<mid>')
def get_medical_record_from_patient(id,mid):
    pass ##return render_template('medical_record.html',medical_record=medical_record)

@api.route('/patients/<id>/physicians')
def get_patient_physicians(id):
    pass ##return render_template('users_list.html',users=users) 

@api.route('/patients/<id>/physicians/<pid>')
def get_patient_physician(id,pid):
    pass #return render_template('profile.html',user=user) 
  


@api.route('/physicians')
def get_physicians():
    pass## return render_template('users_list.html',users=users)

@api.route('/physicians/<pid>')
def get_physician(pid):
    pass ##return render_template('profile.html', user=user)

@api.route('/physicians/<pid>/patients')
def get_physician_patients(pid):
    pass    ##return render_template('users_list.html',users=users)

@api.route('/physicians/<pid>/patients/<id>')
def get_physician_patient(pid, id):
    pass ##return render_template('users_list.html',user=user) 

@api.route('/physicians/<pid>/patients/<id>/medical_records')
def get_medical_records_from_physician(pid,id):
    pass ##return render_template('medical_records.html',medical_records=medical_records)

@api.route('/physicians/<pid>/patients/<id>/medical_records<mid>')
def get_medical_record_from_physician(id,pid,mid):
    pass ##return render_template('medical_record.html',medical_record=medical_record) 

@api.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404

