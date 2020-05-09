from flask import Blueprint, request, redirect, render_template, flash, url_for
#from flask_jwt import jwt_required, current_identity
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from models import db, Med_Institution, User, Physician, Patient, Appointment, Med_Record, Release_Form
from werkzeug.security import generate_password_hash, check_password_hash


import datetime
## consider when doctor or patient deleted, is it deleted from other tables

##remember to configure flash cards



api = Blueprint('api', __name__)


@api.route('/')
def index():
    user=None
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
    logout_user()
    flash("You have been successfully logged out.")
    return redirect(url_for('.index'))

##Profiles are created when registered. This method deals with reading and updating profiles
@api.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    user=None
    if current_user.type == 'patient':
        user=Patient.query.get(current_user.username)
    else: ##current_user.type == 'physician':
        user=Physician.query.get(current_user.username)
    
    if request.method == 'GET':
        return render_template('/users_layout/profile.html', user=user)

    else: ## request.method == 'POST' for Updating profile:
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

    
## This method deals with deletion of a user account.
@api.route('/delete')
def delete_user():
    user=User.query.get(current_user.username)
    name=user.name
    db.session.delete(user)
    db.session.commit()
    flash(f"{name} has been successfully deleted.")
    return redirect('.logout')
        

## this method is to allow a physician to be able to see all of their patients. If a patient uses this url, they are redirected to their profile
@api.route('/patients/<username>')
@login_required
def get_patient(username,uname):
    
    if current_user.username==username and current_user.type=='patient':
        return redirect(url_for('.profile'))

    elif current_user.type=='physician':
        patient=None
        appointment=Appointment.query.filter_by(physician_username=current_user.username, patient_username=username).first()
        if appointment:
            patient=appointment.patient
        else:
            flash("Invalid patient.")

    return render_template('/users_layout/profile.html', user=patient)


##This method allows a patient to view and create their medical record. If exists, patient or physician may edit the medical records in distinct ways.
## Medical records cannot be deleted for legal reasons. Access, however, to physicians is controlled through the Release_Form class
@api.route('/patients/<username>/medical_record', methods=['GET','POST'])
@login_required
def medical_record(username):

    if request.method =='POST':
        data = request.form
        if current_user.type=='patient' and current_user.username==username:  
            ## checking if medical_record for patient already exists
            med_record = Med_Record.query.filter_by(patient_username=current_user.username).first()
            if not med_record:
                ## med_record does not exist; so create it
                current_problem = data['current_problem'] 
                history = data['history']                
                med_record = Med_Record(patient_username = current_user.username,current_problem=current_problem, history=history)
                db.session.add(med_record)
                db.session.commit()
                flash('Medical Record has been created.')
            else: ##update
                if 'current_problem' in data:                
                    current_problem = data['current_problem'] 
                    med_record.history+="\nPast Problem: "+med_record.current_problem+"\n"
                    med_record.current_problem = current_problem
                    db.session.add(med_record)
                    db.session.commit()
                    flash('Medical Record has been updated.')
                else:
                    flash("Nothing to be updated.")
                ## med_record already exists; so update it.  
        
        ## consider if physician is trying to udpdate medical record to add treatment to patient's problem
        elif current_user.type=='physician' and  Release_Form.query.filter_by(physician_username=current_user.username, patient_username=username).first():
            if 'current_treatment' in data:
                current_treatment=data['current_treatment'] 
                med_record = Med_Record.query.filter_by(patient_username=username).first()
                med_record.history += "\n Past Treament: " + med_record.current_treatment+"\n"
                med_record.treatment = current_treatment
                db.session.add(med_record)
                db.session.commit()
                flash(f'Medical Record for patient {username} has been updated.')
            else:
                flash('No treatment entered to be updated.')

        else:
            flash('You are not authorized to perform this action.')
        return redirect(url_for('.medical_record'))         ##come back and deal with logic to 

    else: ## if GET request
        med_record=None
        if current_user.type=='patient' and current_user.username==username:            
            med_record=Med_Record.query.filter_by(patient_username=current_user.username).first()
        elif current_user.type=='physician' and Release_Form.query.filter_by(physician_username=current_user.username, patient_username=username).first():
            med_record = Med_Record.query.filter_by(patient_username=username).first()
        if med_record is None:
            username=None
            flash ("You are not authorized to perform this action.")              
        return render_template('/users_layout/medical_record.html',med_record=med_record, username=username)  # do logic and check if med_records



    '''
    else:
        
        if request.method == 'PUT':
            data = request.form
            if current_user.type=='patient' and current_user.username==username:    
                if 'current_problem' in data:                
                    current_problem = data['current_problem'] 

                    med_record = Med_Record.query.filter_by(patient_username=current_user.username).first  #med record must exist since it is created at signup
                    med_record.history+="\nPast Problem: "+med_record.current_problem+"\n"
                    med_record.current_problem = current_problem
                    db.session.add(med_record)
                    db.session.commit()
                    flash('Medical Record has been updated.')
                    

            elif current_user.type=='physician' and Appointment.query.filter_by(physician_username=current_user.username, patient_username=username).first():
                if 'current_treatment' in data:
                    current_treatment=data['current_treatment'] 
                    med_record = Med_Record.query.filter_by(patient_username=username).first()
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
    '''
## We will use query parameters to achieve Retrieval for various appointments for a user
@api.route('/appointments', methods=['GET','POST'])
@login_required
def appointments():

    if request.method == 'POST': ##create new appointment
        data = request.form
        date = datetime.datetime.strptime(data['date'],"%Y-%m-%d %H:%M:%S")
        ## only a patient can set an appointment
        if current_user.type=='patient':
            appointment = Appointment(physician_username=data['physician_username'], patient_username=data['patient_username'], date = date)
            release_form = Release_Form(physician_username=data['physician_username'], patient_username=data['patient_username'])       #when create an appointent you must sign release form
            db.session.add(appointment)
            db.session.add(release_form)
            db.commit()
            flash(f"Appointment has been set to {data['date']}")
        else:
            flash('Cannot set an Appointment. You are not authorized to perform this action.')
        return redirect(url_for('.appointments'))
        
    else: ## get appointments based on query params
        
        date = request.args.get('date') 
        if date:
            valid_date=True
            try:
                date=date.strip()
                start_date=date+' 00:00:00'
                end_date=date+' 23:59:59'
                start_date=datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                print("value error",e)
                valid_date=False

        username = request.args.get('user')
        ## determine which is physician or which is patient
        if current_user.type == 'patient':
            physician_username=username
            patient_username=current_user.username
        else:
            physician_username=current_user.username
            patient_username=username

        if username and date and valid_date:
            appointments = Appointment.query.filter(Appointment.physician_username==physician_username, Appointment.patient_username==patient_username,
                            Appointment.date>=start_date, Appointment.date<=end_date).all()
        elif username:    
            appointments = Appointment.query.filter_by(physician_username=physician_username, patient_username=patient_username).all()
        elif date and valid_date:
            if current_user.type == 'patient':
                appointments = Appointment.query.filter(Appointment.patient_username==current_user.username,
                                 Appointment.date>=start_date, Appointment.date<=end_date).all()
            else:
                appointments = Appointment.query.filter(Appointment.physician_username==current_user.username,
                                 Appointment.date>=start_date, Appointment.date<=end_date).all()
        else:
            if current_user.type=='patient':
                appointments = Patient.query.get(current_user.username).appointments  ## come back and order by newest
            else:
                appointments = Physician.query.get(current_user.username).appointments ## come back and order by newest

        return render_template('/users_layout/appointment_list.html',appointment=appointments)


## Besides viewing, a patient can change and delete appointments; whereas, a physician can only  change appoinments
#GET with a delete query parameter will be used for delete. Post will be used for update
@api.route('/appointments/<id>', methods=['GET','POST'])
@login_required
def appointment(id):    
    if current_user.type == 'patient':
        appointment = Appointment.query.filter_by(patient_username = current_user.username,id=id).first()
    else:
        appointment = Appointment.query.filter_by(physician_username = current_user.username,id=id).first()

    if appointment:    
        ##change appointment
        if request.method == 'POST':
            
            data = request.form  
            ##consider if date is given. For our app, to update, a date must be specified; else it means deletion, which can only be done by a patient.
            if 'new_date' in data:              
                new_date = datetime.datetime.strptime(data['new_date'],"%Y-%m-%d %H:%M:%S")               
                appointment.date = new_date
                db.session.add(appointment)
                db.session.commit()
                flash(f"Appointment has been rescheduled to {data['new_date']}")
            else:
                flash("Nothing to be updated.")
        else:
            delete = request.args.get('delete')
            if delete=='True' and current_user.type=='patient':
                db.session.delete(appointment)
                db.session.commit()
                flash("Appointment has been cancelled.")
            elif delete=='True':
                flash('Cannot delete an Appointment. You are not authorized to perform this action.')
                return redirect(url_for('.unauthorize'))
            else:
                flash('Nothing to be done.')
               
    else:
        flash ('No appointment exists. Here is a list of your appointments')

    return redirect(url_for('.appointments'))
    


        


'''
@api.route('/physicians/<uname>/appointments')
@login_required
def get_physician_appointment(uname):
    appointments=None
    if current_user.type=='physician' and current_user.username==uname :
        appointments = Physician.query.get(uname).appointments
    return render_template('/users_layout/appointment_list.html',appointment=appointments)
'''


@api.route('/my_physicians')
@login_required
def get_my_physicians():
    physicians=[]
    used=set()
    if current_user.type=='patient':
        appointments = Patient.query.get(current_user.username).appointments
        if appointments:
            for appointment in appointments:
                if not appointment.physician_username in used:
                    used.add(appointment.physician_username)
                    physicians.append(appointment.physician)
        return render_template('/users_layout/users_list.html',users=physicians, title='My Physicians') 
    else:
        flash('Invalid Request. You are not a patient')
        return redirect(url_for('.index'))

@api.route('/my_patients')
@login_required
def get_my_patients():
    patients=[]
    used=set()
    if current_user.type=='physician':
        appointments = Physician.query.get(current_user.username).appointments
        for appointment in appointments:
            if not appointment.patient_username in used:
                used.add(appointment.patient_username)
                patients.append(appointment.patient)
        return render_template('/users_layout/users_list.html',users=patients, title='My Patients')
    else:
        flash('Invalid Request. You are not a physician.')
        return redirect(url_for('.index'))

@api.route('/physicians')
def get_physicians():
    physicians=Physician.query.all()
    return render_template('/users_layout/users_list.html',users=physicians, title="Physicians Listing")

@api.route('/physicians/<uname>')
def get_physician(uname):    
    physician = Physician.query.filter_by(username = uname).first()
    return render_template('/users_layout/profile.html', user=physician)


@api.route('/med_institutions')
def get_med_institutions():
    med_institutions = Med_Institution.query.all()
    return render_template('/users_layout/med_institution_list.html',med_institutions=med_institutions)

'''
@api.route('/med_institutions/<id>')
def get_med_institution(id):
    med_institution = Med_Institution.query.get(id)
    return render_template('/users_layout/med_institution.html',med_institution=med_institution)
'''

## This method allows for the viewing of release forms for both physicians and patients.
@api.route('/release_forms')
@login_required
def get_releases():

    if current_user.type=='patient':
        release_forms = Release_Form.query.filter_by(patient_username=current_user.username).all()
    else:
        release_forms = Release_Form.query.filter_by(physician_username=current_user.username).all()
    return render_template('users_layout/releases.html',release_forms=release_forms)
    
##Pnly a patient can remove a release form
@api.route('/release_forms/<id>')
@login_required
def cancel_releases():

    delete = request.args.get('delete')
    
    if delete=='True':

        if current_user.type=='patient':
            release_form = Release_Form.query.filter_by(patient_username=current_user.username, id=id).first()
            if release_form:
                ## appointmentDate
                date = Appointment.query.filter_by(patient_username=current_user.username,physician_username = release_form.physician_username).order_by(id.desc()).first().date
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
            return redirect(url_for('.unauthorize'))
    else: ##show all release
        return url_for('.get_releases')


@api.route('/about')
def get_about():
    return render_template('/front_layout/about.html')


@api.errorhandler(401)
@api.route('/unauthorize')
def unauthorize(e):
    flash('You are not authorize to perform this action')
    return render_template('/error_handling/unauthorize.html'),401
