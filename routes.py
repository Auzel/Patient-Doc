from flask import Blueprint, request, redirect, render_template, flash, url_for, current_app, session, abort
#from flask_jwt import jwt_required, current_identity
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from models import db, Med_Institution, User, Physician, Patient, Appointment, Med_Record, Release_Form
from forms import Login, SignUp, Physician_SignUp, Booking
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime
import os

UPLOAD_FOLDER = './static/img/user_uploads'


api = Blueprint('api', __name__)

    


@api.route('/')
def index():
    user=None
    if current_user.is_authenticated:
        user=current_user
        if user.num_visits==0:
            user.num_visits+=1
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('.profile'))
    return render_template('/main_layout/home.html', user=user,  title="Home") 


#include <link href="style2.css" type="text/css" rel="stylesheet">
## send title for templates
@api.route('/signup', methods=['GET', 'POST'])
def signup():
    ### Need to make slight change for physician
    signup = SignUp()
    physician_signup = Physician_SignUp()

    if signup.validate_on_submit():     
        
        data=request.form
        type = data['type']

        if type == 'physician' and not physician_signup.validate_on_submit():
            flash("Please fill in all the fields.")
            return redirect(request.url)
                   
        names = data['name'].split()

        fname=names[0]
        ##retrieve last name
        if len(names) >= 2:            
            lname=names[1]
        else: ##no lname given
            lname=""

        fname = fname[:20] if len(fname)>20 else fname
        lname = lname[:20] if len(lname)>20 else lname
        
        DOB = datetime.datetime.strptime(data['DOB'],"%Y-%m-%d")

        
        if type=='patient':
            user = Patient(fname = fname, lname=lname, email=data['email'], address=data['address'], date_of_birth=DOB)
          
        elif type=='physician':
            ##deal with dereference key to an integer
            ##remember to add med_id to variable
            user = Physician(fname = fname, lname=lname, email=data['email'], address=data['address'], date_of_birth=DOB,
            type1=data['physician_type'], degree=data['degree'],place_of_education = data['place_of_education'] ) 

            ##Store MedicalFile
            file = request.files['license']        
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            
        user.set_password(data['password']) # set password                    

        try:
            db.session.add(user) # save new user
            db.session.commit()
        except IntegrityError as e : # attempted to insert a duplicate user
            print('problem: ',e)
            db.session.rollback()
            flash('Email already exists')
            return redirect(url_for('.signup'))
        flash('Account Created!')
        return redirect(url_for('.login'))      

    return render_template('/main_layout/signup.html', signup=signup, physician_signup=physician_signup, title="Sign Up")


@api.route('/login', methods=['GET', 'POST'])
def login():
    ##when logged in he is redirected to the user-specific page where he can now view his profile/latest medical report or medical reports
    login = Login()
    if login.validate_on_submit(): ##request.method == 'POST' and validate:
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            if request.form.get("remember_me"):
                login_user(user, remember=True )
            else:
                login_user(user)
            flash('Logged in successfully.') 
            
            next = request.args.get('next')

            ##if not is_safe_url(next):
                ##return abort(400)
            return redirect(next or url_for('.index'))

        else:
            flash('Invalid email or password') # send message to next page    
            return redirect(url_for('.login')) 
    return render_template('/main_layout/login.html', login=login,  title="Login")


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
    basic = SignUp()
    extra = Physician_SignUp()
    user=None
    if current_user.type == 'patient':
        user=Patient.query.get(current_user.id)
    else: ##current_user.type == 'physician':
        user=Physician.query.get(current_user.id)
    

    update=request.args.get('update')
    if request.method == 'GET' :
        return render_template('/main_layout/profile.html', title="Profile", basic=basic, extra=extra, user=user, update=update )


    else: ## request.method == 'POST' for Updating profile:
        data = request.form
        if 'name' in data:
            fname,lname=data['fname'].split()
            fname = fname[:20] if len(fname)>20 else fname
            lname = lname[:20] if len(lname)>20 else lname

            user.fname = fname    
            user.lname = lname
        if 'password' in data:
            user.set_password(data['password'])
        if 'DOB' in data:
            DOB = datetime.datetime.strptime(data['DOB'],"%Y-%m-%d")
            user.date_of_birth=DOB   
        if 'address' in data:
            user.address = data['address']
        
        if user.type == 'physician':
            if 'type1' in data:
                user.type1=data['type1']
            if 'degree' in data:
                user.degree=data['degree']
            if 'education' in data:
                user.education = data['education'] 


    if (user.type == 'patient' and  basic.validate_on_submit()) or (user.type == 'patient' and extra.validate_on_submit()):          
        data=request.form
        
        ##patient section
        if 'email' in data: 
            user.email = data['email']
        if 'password' in data:
            if len(data['password']) >= 7 and len(data['password'])<=20:
                user.set_password(data['password'])
        if 'DOB' in data:
            DOB = datetime.datetime.strptime(data['DOB'],"%Y-%m-%d")
            user.date_of_birth=DOB           
        if 'address' in data:
            user.address = data['address']

        ##physician section
        if user.type == 'physician':
            if 'type1' in data:
                user.type1=data['type1']
            if 'degree' in data:
                user.degree=data['degree']
            if 'place_of_education' in data:
                user.education = data['place_of_education'] 
            if 'med_key' in data:
                user.med_key = data['med_key']

         ## note above that name, type nor medical license can be changed                        

        try:
            db.session.add(user) # save new user
            db.session.commit()
        except IntegrityError as e : # attempted to insert a duplicate user
            print('problem: ',e)
            db.session.rollback()
            flash('Email already exists')
            return redirect(url_for('.signup'))
        flash('Profile Updated.')
    else:
        flash("Update couldn't be completed. Please ensure you have inputted valid data.")
    return redirect(url_for('.profile'))
    
## This method deals with deletion of a user account.
@api.route('/delete')
@login_required
def delete_user():
    user=User.query.get(current_user.id)
    name=user.fname + " " + user.lname
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash(f"{name} has been successfully deleted.")
    return redirect(url_for('.index'))

        

## this method is to allow a physician to be able to see all of their patients. If a patient uses this url, they are redirected to their profile
@api.route('/patients/<id>')
@login_required
def get_patient(id):
    patient=None

    basic = SignUp()
    extra = Physician_SignUp()

    if str(current_user.id)==id and current_user.type=='patient':
        return redirect(url_for('.profile'))

    elif current_user.type=='physician':
        appointment=Appointment.query.filter_by(physician_id=current_user.id, patient_id=id).first()
        if appointment:
            patient=appointment.patient
            return render_template('/main_layout/profile.html', title="Profile", basic=basic, extra=extra, user=patient, update='false')

    return redirect(url_for('.unauthorized'))


##This method allows a patient to view and create their medical record. If exists, patient or physician may edit the medical records in distinct ways.
## Medical records cannot be deleted for legal reasons. Access, however, to physicians is controlled through the Release_Form class
@api.route('/patients/<id>/medical_record', methods=['GET','POST'])
@login_required
def medical_record(id):

    if request.method =='POST':
        data = request.form
        if current_user.type=='patient' and str(current_user.id)==id:  
            ## checking if medical_record for patient already exists
            med_record = Med_Record.query.filter_by(patient_id=current_user.id).first()
            if not med_record:
                ## med_record does not exist; so create it
                current_problem = data['current_problem'] 
                history = data['history']                
                med_record = Med_Record(patient_id = current_user.id,current_problem=current_problem, history=history)
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
        elif current_user.type=='physician' and  Release_Form.query.filter_by(physician_id=current_user.id, patient_id=id).first():
            if 'current_treatment' in data:
                current_treatment=data['current_treatment'] 
                med_record = Med_Record.query.filter_by(patient_id=id).first()
                med_record.history += "\n Past Treament: " + med_record.current_treatment+"\n"
                med_record.treatment = current_treatment
                db.session.add(med_record)
                db.session.commit()
                flash(f'Medical Record for patient has been updated.')
            else:
                flash('No treatment entered to be updated.')

        else:
            flash('You are not authorized to perform this action.')
        return redirect(url_for('.medical_record'))         ##come back and deal with logic to 

    else: ## if GET request

        med_record= None
        if current_user.type=='patient' and str(current_user.id)==id:            
            med_record=Med_Record.query.filter_by(patient_id=current_user.id).first()
        elif current_user.type=='physician' and Release_Form.query.filter_by(physician_id=current_user.id, patient_id=id).first():
            med_record = Med_Record.query.filter_by(patient_id=id).first()
        if med_record is None:            
            return redirect(url_for('.unauthorized'))   
       
        return render_template('/main_layout/medical_record.html',med_record=med_record)  # do logic and check if med_records

## We will use query parameters to achieve Retrieval for various appointments for a user
@api.route('/appointments', methods=['GET','POST'])
@login_required
def appointments():

    booking = Booking()

    if request.method == 'POST': ##create new appointment
        data = request.form
        date = datetime.datetime.strptime(data['date'],"%Y-%m-%d")
        time = datetime.datetime.strptime(data['date'],"%H:%M:%S")

        ##overrite date to include time
        date = datetime.datetime.combine(date,time)
        ## only a patient can set an appointment
        if current_user.type=='patient':
            appointment = Appointment(physician_id=data['physician_id'], patient_id=data['patient_id'], date = date)
            release_form = Release_Form(physician_id=data['physician_id'], patient_id=data['patient_id'])       #when create an appointent you must sign release form
            db.session.add(appointment)
            db.session.add(release_form)
            db.commit()
            flash(f"Appointment has been set to {data['date']}")
        else:
            flash('Cannot set an Appointment. You are not authorized to perform this action.')
        return redirect(url_for('.appointments'))
        
    else: ## get appointments based on query params
        update=request.args.get('update') ## store if update was requeted

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

        id = request.args.get('user_id')
        ## determine which is physician or which is patient
        if current_user.type == 'patient':
            physician_id=id
            patient_id=current_user.id
        else:
            physician_id=current_user.id
            patient_id=id

        if id and date and valid_date:
            appointments = Appointment.query.filter(Appointment.physician_id==physician_id, Appointment.patient_id==patient_id,
                            Appointment.date>=start_date, Appointment.date<=end_date).all()
        elif id:    
            appointments = Appointment.query.filter_by(physician_id=physician_id, patient_id=patient_id).all()
        elif date and valid_date:
            if current_user.type == 'patient':
                appointments = Appointment.query.filter(Appointment.patient_id==current_user.id,
                                 Appointment.date>=start_date, Appointment.date<=end_date).all()
            else:
                appointments = Appointment.query.filter(Appointment.physician_id==current_user.id,
                                 Appointment.date>=start_date, Appointment.date<=end_date).all()
        else:
            if current_user.type=='patient':
                appointments = Patient.query.get(current_user.id).appointments  ## come back and order by newest
            else:
                appointments = Physician.query.get(current_user.id).appointments ## come back and order by newest

        return render_template('/listing_layout/appointment_list.html',appointment=appointments, update=update, booking=booking)


## Besides viewing, a patient can change and delete appointments; whereas, a physician can only  change appoinments
#GET with a delete query parameter will be used for delete. Post will be used for update
@api.route('/appointments/<id>', methods=['GET','POST'])
@login_required
def appointment(id):    
    if current_user.type == 'patient':
        appointment = Appointment.query.filter_by(patient_id = current_user.id,id=id).first()
    else:
        appointment = Appointment.query.filter_by(physician_id = current_user.id,id=id).first()

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
                return redirect(url_for('.unauthorized'))
            else:
                flash('Nothing to be done.')
               
    else:
        flash ('No appointment exists. Here is a list of your appointments')

    return redirect(url_for('.appointments'))
    


        

@api.route('/my_physicians')
@login_required
def get_my_physicians():
    physicians=[]
    used=set()
    if current_user.type=='patient':
        appointments = Patient.query.get(current_user.id).appointments
        if appointments:
            for appointment in appointments:
                if not appointment.physician_id in used:
                    used.add(appointment.physician_id)
                    physicians.append(appointment.physician)
        return render_template('/listing_layout/users_list.html',users=physicians, title='My Physicians') 
    else:
        flash('Invalid Request. You are not a patient')
        return redirect(url_for('.index'))

@api.route('/my_patients')
@login_required
def get_my_patients():
    patients=[]
    used=set()
    if current_user.type=='physician':
        appointments = Physician.query.get(current_user.id).appointments
        for appointment in appointments:
            if not appointment.patient_id in used:
                used.add(appointment.patient_id)
                patients.append(appointment.patient)
        return render_template('/listing_layout/users_list.html',users=patients, title='My Patients')
    else:
        flash('Invalid Request. You are not a physician.')
        return redirect(url_for('.index'))

@api.route('/physicians')
def get_physicians():
    physicians=Physician.query.all()
    return render_template('/listing_layout/users_list.html',users=physicians, title="Physicians Listing")

@api.route('/physicians/<id>')
def get_physician(id):    
    physician = Physician.query.filter_by(id = id).first()
    return render_template('/listing_layout/profile.html', user=physician)


@api.route('/med_institutions')
def get_med_institutions():
    med_institutions = Med_Institution.query.all()
    return render_template('/listing_layout/med_institution_list.html',med_institutions=med_institutions)

## This method allows for the viewing of release forms for both physicians and patients.
@api.route('/release_forms')
@login_required
def get_releases():

    if current_user.type=='patient':
        release_forms = Release_Form.query.filter_by(patient_id=current_user.id).all()
    else:
        release_forms = Release_Form.query.filter_by(physician_id=current_user.id).all()
    return render_template('listing_layout/releases.html',release_forms=release_forms)
    
##Pnly a patient can remove a release form
@api.route('/release_forms/<id>')
@login_required
def cancel_releases():

    delete = request.args.get('delete')
    
    if delete=='True':

        if current_user.type=='patient':
            release_form = Release_Form.query.filter_by(patient_id=current_user.id, id=id).first()
            if release_form:
                ## appointmentDate
                date = Appointment.query.filter_by(patient_id=current_user.id,physician_id = release_form.physician_id).order_by(id.desc()).first().date
                ##check if above works I just need the descending of records to occur

                #only allow deletion if past appointment date
                if datetime.datetime.now() > date: 
                    db.session.delete(release_form)
                    db.session.commit()
                    flash("Doctor is no longer able to view your medical Records.") ##Specify doctor name later
                else:
                    flash("Cannot remove release form when you have a pending appointment date. If you would like to remove the release form, first cancel the appointment")
            else:
                flash("Release Agreement does not exists.")
            return url_for('.get_releases')
        else:
            return redirect(url_for('.unauthorized'))
    else: ##show all release
        return url_for('.get_releases')


@api.route('/about')
def get_about():
    return render_template('/main_layout/about.html', title="About Us")

@api.route('/unauthorized')
def unauthorized():
    return render_template('/error_handling/unauthorized.html'),401