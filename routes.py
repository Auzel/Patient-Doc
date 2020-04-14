from flask import Blueprint, request, render_template
from flask_jwt import jwt_required, current_identity

## consider when doctor or patient deleted, is it deleted from other tables
## do routes for ? queries
## account for status codes
api = Blueprint('api', __name__)

@api.route('/')
def index():
    return render_template('home.html')

@api.route('/signup')
def signup():
    pass ##return render_template('signup.html',form=form)

@api.route('/login')
def login():
    pass ##return render_template('login.html',form=form)

@api.route('/users')
def get_users():
    pass ##return render_template('users_list.html',users=users)

@api.route('/patients')
def get_patients():
    pass##  return render_template('users_list.html',users=users)


@api.route('/patients/<id>')
def get_patient(id):
    pass   ##   return render_template('profile.html',user=user)

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

