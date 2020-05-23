import json
from authlib.integrations.flask_client import OAuth
#from flask_oauthlib.client import OAuth as OAuth2
from flask_cors import CORS
from flask import Flask
from flask_login import LoginManager, current_user, login_user
##from flask_jwt import JWT, jwt_required,current_identity
from flask import Blueprint, request, redirect, render_template, flash, url_for, session
from datetime import timedelta
from routes import api
from models import db, Med_Institution, User, Physician, Patient, Med_Record, Release_Form
from forms import Login, SignUp, Physician_SignUp, Booking, Med_Record_SetUp


from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

import sys


UPLOAD_FOLDER = './static/img/user_uploads'

''' Begin Boilerplate Code '''


''' Begin Flask Login Functions '''
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

''' End Flask Login Functions '''


def create_app():
    app = Flask(__name__, static_url_path='')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://b14123372f4b3e:f699ac44@us-cdbr-east-06.cleardb.net/heroku_445c2bc68d2f401'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://QyXdkevbhjDtgY2:h43rn8tovLk8okG3Rwyt@patientdoc.coe5ekrasfr6.us-west-1.rds.amazonaws.com/PatientDocDB'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://QyXdkevbhjDtgY2:h43rn8tovLk8okG3Rwyt@patientdocdb.coe5ekrasfr6.us-west-1.rds.amazonaws.com:5432/PatientDoc'
    #app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SECRET_KEY'] = 'PaT|nt-D0CT0R@App'    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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


##External routes
##Start Google Login
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

##end google login

##start google authentication
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

@app.route('/google_auth')
def google_auth():

    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(access_type='offline')

    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
    state = session['state']

    flow = Flow.from_client_secrets_file( CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    #flow = Flow.from_client_config(dict, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    flash("All subsequent appointments shall be reflected on your google calendar.")
    return redirect(url_for('api.appointments'))




def credentials_to_dict(credentials):
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

##end google authentication







@app.errorhandler(404)
def page_not_found(e):
    return render_template('/error_handling/error404.html'), 404


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)


