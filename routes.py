from flask import Blueprint, request, redirect, render_template
from flask_jwt import jwt_required, current_identity

## consider when doctor or patient deleted, is it deleted from other tables
## do routes for ? queries
## account for status codes
api = Blueprint('api', __name__)

@api.route('/')
def index():
    link_1 = "/front_layout/login"
    link_1name = "Login"
    link_2 = "/front_layout/signup"
    link_2name="Sign Up"
    name ="Home"
    return render_template('/front_layout/home.html', 
    link_1=link_1, link_1name=link_1name, 
    link_2=link_2, link_2name=link_2name,
    name=name)

@api.route('/front_layout/signup', methods=['Get', 'POST'])
def signup():
    name="Sign up"
    link_1 = "/front_layout/login"
    link_1name = "Login"
    ### get data and post to database...todo
    if request.method == 'POST':
        req=request.form
        print(req.get('fname'))
        return redirect(request.url)
    return render_template('/front_layout/signup.html', 
    link_1=link_1, link_1name=link_1name, name=name)

@api.route('/front_layout/login')
def login():
    name="Login"
    link_2 = "/front_layout/signup"
    link_2name="Sign Up"
    #Uncomment the following code then go to the login page and see how the app behaves(it assumes that tom is logged in)
    ##when logged in he is redirected to the user-specific page where he can now view his profile/latest medical report or medical reports
    """if request.method == 'GET':
        #req=request.form
        name="Home"
        username = "tom"
        link_1 = f"/users_layout/profile/{username}"
        link_1name = "Profile"
        link_2 = "/users_layout/medical_records"
        link_2name="Medical Record"
        return render_template('/front_layout/home.html',
        link_1=link_1, link_1name=link_1name, 
        link_2=link_2, link_2name=link_2name,
        name=name)"""
    return render_template('/front_layout/login.html',
    link_2=link_2, link_2name=link_2name, name=name)

@api.route('/users_layout/profile')
def profile():
    name="Profile"
    users=None
    return render_template('/users_layout/profile.html',name=name)

@api.route('/users_layout/profile/<username>')
## NOTE medical records link should only appear if user is valid, it appears now just for functionality.
def user_profile(username):
    link_1 = "/users_layout/medical_records" ##link should read /users_layout/profile/patients/<id>/medical_records to get userspecific data
    link_1name = "Medical Records"
    name="Profile"
    users=None
    #if username in ##users_list/database:
        #users = User[username]
    return render_template('/users_layout/profile.html',
    link_1=link_1, link_1name=link_1name, 
    name=name,users=users, username=username)


@api.route('/users')
def get_users():
    pass ##return render_template('users_list.html',users=users)

@api.route('/patients')
def get_patients():
    pass##  return render_template('users_list.html',users=users)


@api.route('/patients/<id>')
def get_patient(id):
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

