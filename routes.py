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
        print('hi')
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

@api.route('/profile',methods=['GET','PUT','DELETE'])
@login_required
def profile():
    user=None
    if current_user.type == 'patient':
        user=Patient.query.get(current_user.username)
    else: ##current_user.type == 'physician':
        user=Physician.query.get(current_user.username)
    
    if request.method == 'GET':
        return render_template('/users_layout/profile.html', user=user)

    elif request.method == 'PUT':
        data = request.form
        if 'fname' in data:
            user.fname = data['fname'] 
        if 'lname' in data:
            user.lname = data['lname'] 
        if 'password' in data:
            user.set_password(data['password'])
        if 'DOB' in data:
            user.date_of_birth=data['DOB']
        if 'address' in data:
            user.address = data['address']
        if 'email' in data:
            user.email = data['email']
        
        if user.type == 'physician':
            if 'type1' in data:
                user.type1=data['type1']
            if 'degree' in data:
                user.degree=data['degree']
            if 'education' in data:
                user.education = data['education'] 
        
        db.session.add(user)
        db.session.commit()        ## ask are you sure in javascript
        flash("Profile Updated.")
        return redirect(url_for('.profile'))

    else: ## logic for delete
        name=user.name
        db.session.delete(user)
        db.session.commit()
        flash(f"{name} has been successfully deleted.")
        return redirect('.logout')
        

@api.route('/patients/<username>')
@login_required
def get_patient(username,uname):
    
    if current_user.username==username and current_user.type=='patient':
        return redirect(url_for('.profile'))

    elif current_user.type=='physician':
        patient=None
        appointment=Appointment.query.filter(physician_username=current_user.username, patient_username=username).first()
        if appointment:
            patient=appointment.patient

    return render_template('/users_layout/profile.html', user=patient)


@api.route('/patients/<username>/medical_record', methods=['GET''POST','PUT','DELETE'])
@login_required
def medical_record(username,uname):

    if request.method =='POST':
        data = request.form
        if current_user.type=='patient' and current_user.username==username:    
            current_problem = data['current_problem'] 
            history = data['history']
            
            med_record = Med_Record(patient_username = current_user.username,current_problem=current_problem, history=history)
            db.session.add(med_record)
            db.session.commit()
            flash('Medical Record has been created.')
        else:
            flash('Cannot created Medical Record. You are not authorized to perform this action.')
        return redirect(url_for('.medical_record'))         ##come back and deal with logic to 

    else:
        if request.method == 'PUT':
            data = request.form
            if current_user.type=='patient' and current_user.username==username:    
                if 'current_problem' in data:                
                    current_problem = data['current_problem'] 

                    med_record = Med_Record.query(patient_username=current_user.username)  #med record must exist since it is created at signup
                    med_record.history+="\nPast Problem: "+med_record.current_problem+"\n"
                    med_record.current_problem = current_problem
                    db.session.add(med_record)
                    db.session.commit()
                    flash('Medical Record has been updated.')
                    

            elif current_user.type=='physician' and Appointment.query.filter(physician_username=current_user.username, patient_username=username).first():
                if 'current_treatment' in data:
                    current_treatment=data['current_treatment'] 
                    med_record = Med_Record.query(patient_username=username)
                    med_record.history += "\n Past Treament: " + med_record.current_treatment+"\n"
                    med_record.treatment = current_treatment
                    db.session.add(med_record)
                    db.session.commit()
                    flash('Medical Record has been updated')
                else:
                    flash('No treatment entered to be updated.')
            else:
                flash ('Cannot update Medical Record. You are not authorized to perform this action.')
            return redirect(url_for('.medical_record'))

        if request.method == 'DELETE':
            if current_user.type=='patient' and current_user.username==username: 
                 med_record = Med_Record.query(patient_username=current_user.username)
                 db.session.delete(med_record)
                 db.session.commit()
                 flash('Medical Record has been deleted.')
            return redirect(url_for('.index'))

        else: #if request.method == 'GET': 
            username = None 
            med_record=None
            if current_user.type=='patient' and current_user.username==username:    
                med_record=Med_Record.query(patient_username=current_user.username)
            elif current_user.type=='physician' and Appointment.query.filter(physician_username=current_user.username, patient_username=username).first():
                med_record = Med_Record.query(patient_username=username)  
            if med_record == None:
                flash ("Cannot view Medical Record. You are not authorized to perform this action.'")              
            return render_template('/users_layout/medical_record.html',med_record=med_record, username=username)  # do logic and check if med_records
    
   
@api.route('/patients/<username>/appointment/<date>')
@api.route('/physicians/<uname>/patients/<username>/appointment/<date>', methods=['GET''POST','PUT','DELETE'])
@login_required
def appointment(username,uname,date):
  

    if request.method == 'POST':
        data = request.form
        date = datetime.datetime.strptime(data['date'],"%Y-%m-%d")
        if current_user.type=='patient' and current_user.username==username:
            appointment = Appointment(patient_username=data['patient_username'],physician_username=['physician_username'], date = date)
            release_form = Release_Form(patient_username=data['patient_username'],physician_username=['physician_username'])       #when create an appointent you must sign release form
            db.session.add(appointment)
            db.session.add(release_form)
            db.commit()
            flash(f"Appointment has been set to {data['date']}")
        else:
            flash('Cannot set an Appointment. You are not authorized to perform this action.')
        return redirect(url_for('.appointment'))

    elif request.method == 'PUT':
        data = request.form
        if (current_user.type=='patient' and current_user.username==username) or (current_user.type=='physician' and current_user.username==uname):
            if date in data:
                date = datetime.datetime.strptime(data['date'],"%Y-%m-%d")           
                appointment = Appointment.query.filter_by(physician_username=uname, patient_username=username,date=date).first()
                if appointment:
                    appointment.date = date
                    db.session.add(appointment)
                    db.session.commit()
                    flash(f"Appointment has been rescheduled to {data['date']}")
                else:
                    flash ('No appointment exists.')
            else:
                flash('A date was not given to change the Appointment date.')
        else:
            flash('Cannot update an Appointment. You are not authorized to perform this action.')
        return redirect(url_for('.appointment'))

    elif request.method == 'DELETE':
        if current_user.type=='patient' and current_user.username==username:
            appointment = Appointment.query.filter_by(physician_username=uname, patient_username=username,date=date).first()
            if appointment:
                release_form = Release_Form.query.filter(patient_username=data['patient_username'],physician_username=['physician_username'])   ## automatically remove release form
                db.session.delete(release_form)
                db.session.delete(appointment)
                db.session.commit()
                flash("Appointment has been cancelled.")
            else:
                flash('No appoinment exists')
        else:
            flash('Cannot delete an Appointment. You are not authorized to perform this action.')

    else: ## GET request
        appointment=None
        if (current_user.type=='patient' and current_user.username==username) or (current_user.type=='physician' and current_user.username==uname):
            appointment = Appointment.query.filter_by(physician_username=uname, patient_username=username,date=date).first()
            return render_template('/users_layout/appointment.html',appointment=appointment)
        else:
            redirect(url_for('.unauthorize'))
        


@api.route('/patients/<username>/appointments')
@login_required
def get_patient_appointments(username):
    appointments=None
    if current_user.type=='patient' and current_user.username==username:
        appointments = Patient.get(username).appointments
    return render_template('/users_layout/appointment_list.html',appointment=appointments)


@api.route('/physicians/<uname>/appointments')
@login_required
def get_physician_appointment(uname):
    appointments=None
    if current_user.type=='physician' and current_user.username==uname :
        appointments = Physician.get(uname).appointments
    return render_template('/users_layout/appointment_list.html',appointment=appointments)


@api.route('/patients/<username>/physicians')
@login_required
def get_patient_physicians(username):
    physicians=[]
    used=set()
    if current_user.type=='patient' and current_user.username==username :
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
    if current_user.type=='physician' and current_user.username==uname:
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
def get_med_institution(id):
    med_institution = Med_Institution.query.get(id)
    return render_template('/users_layout/med_institution.html',med_institution=med_institution)

@api.route('/release_forms')
@login_required
def get_releases():
    release_forms=None
    if current_user.type=='patient':
        release_form = Release_Form(patient_username=current_user.username)
    return render_template('users_layout/releases.html',release_forms=release_forms)

@api.route('/release_forms/<id>',methods=['DELETE'])
@login_required
def remove_release(id):
    if current_user.type=='patient':
        release_form = Release_Form(patient_username=current_user.username, id=id)
        if release_form:
            ## appointmentDate
            date = Appointment.query.filter(patient_username=current_user.username,physician_username = release_form.physician_username).order_by(id.desc()).first().date
            ##check if above works I just need the descending of records to occur

            #only allow deletion if past appointment date
            if datetime.datetime.utcnow() > date: 
                db.session.delete(release_form)
                db.session.commit()
                flash(f"Doctor {release_form.physician_username} is no longer able to view your medical Records.")
            else:
                flash("Cannot remove release form when you have a pending appointment date. If you would like to remove the release form, first cancel the appointment")
        else:
            flash(f"Release Agreement does not exists.")
        return url_for('.get_releases')
    else:
        return redirect(url_for('/unauthorize'))

@api.route('/unauthorize')
def unauthorize():
    flash('You are not authorize to perform this action')
    return render_template('/static/unauthorize.html')

@api.errorhandler(404)
def page_not_found(e):
    return render_template('/static/error404.html'), 404

