import json
from authlib.integrations.flask_client import OAuth
#from flask_oauthlib.client import OAuth as OAuth2
from flask_cors import CORS
from flask import Flask
from flask_login import LoginManager, current_user, login_user
##from flask_jwt import JWT, jwt_required,current_identity
from flask import Blueprint, request, redirect, render_template, flash, url_for
from datetime import timedelta 
from routes import api
from models import db, Med_Institution, User, Physician, Patient, Med_Record, Release_Form



from forms import Login, SignUp, Physician_SignUp, Booking, Med_Record_SetUp


#UPLOAD_FOLDER = 'http://s3.amazonaws.com/patientdoc/'

''' Begin Boilerplate Code '''

''' Begin Flask Login Functions '''
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

''' End Flask Login Functions '''


def create_app():
    app = Flask(__name__, static_url_path='')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b4ab06921840a3:995a5935@us-cdbr-iron-east-01.cleardb.net/heroku_b2abbb44d079db0'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = 'P@T|nt-D0CT0R@App'    
    #app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    #app.config['JWT_EXPIRATION_DELTA'] = timedelta(days = 1)   
    login_manager.init_app(app)
    login_manager.login_view = 'api.login'   
    CORS(app)
    db.init_app(app)
    return app

app = create_app()

app.app_context().push()

app.register_blueprint(api)
''' End Boilerplate Code '''

#oauth = OAuth(app) ##for google

#oauth2 = OAuth2(app) ##for fb


'''
facebook = oauth2.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='2390386897927898',
    consumer_secret='0fbaebf03dbff511a9f4d54b57685bfc',
    request_token_params={'scope': ('email, ')}
)
'''

oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id="397826301896-uhedqe0seh2u3diadhll12vadesm0vhs.apps.googleusercontent.com",
    client_secret="rElDrcUPL4_nFpYxEviTCZsB",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile '},
)



## consider when doctor or patient deleted, is it deleted from other tables

##remember to configure flash cards



##External routesin
@app.route('/google_login')
def google_login():
    
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)
    
   
@app.route('/authorize')
def authorize():    
    user=None
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    userinfo= resp.json()
   
    user = User.query.filter_by(email=userinfo['email']).first()
    if user:            
        login_user(user)
        flash('Logged in successfully.') 
        user.num_visits+=1
        db.session.add(user)
        db.session.commit()

        if user.num_visits==1:  ## first time
            return redirect(url_for('api.index')) ## go to home page

        next = request.args.get('next')

        ##if not is_safe_url(next):
            ##return abort(400)
        return redirect(next or url_for('api.index'))

    else:
        flash('No user associated with this google account. Please register an account first.') # send message to next page    
        return redirect(url_for('api.signup')) 


@app.errorhandler(404)
def page_not_found(e):
    return render_template('/error_handling/error404.html'), 404

@app.route('/app')
def test():
    return app.send_static_file('app.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)


