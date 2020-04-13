import json
from flask_cors import CORS
from flask import Flask, request, render_template
from sqlalchemy.exc import IntegrityError
from flask_jwt import JWT, jwt_required, current_identity
from datetime import timedelta 

from models import db, Med_Institution, User, Physician, Patient, Med_History, Release_Form

''' Begin boilerplate code '''
def create_app():
  app = Flask(__name__, static_url_path='')
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b4ab06921840a3:995a5935@us-cdbr-iron-east-01.cleardb.net/heroku_b2abbb44d079db0'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
  ##app.config['SECRET_KEY'] = "MYSECRET"    
  app.config['JWT_EXPIRATION_DELTA'] = timedelta(days = 7)   
  CORS(app)
  db.init_app(app)
  return app

app = create_app()

app.app_context().push()

''' End Boilerplate Code '''

''' Set up JWT here '''
def authenticate(uname, password):
  user=User.query.filter_by(username=uname).first()
  if user and user.check_password(password):
    return user

def identity(payload):
  return User.query.get(payload['identity'])
  
jwt = JWT(app,authenticate,identity)
''' End JWT Setup '''


@app.route('/')
def index():
  return render_template('home.html')

@app.route('/app')
def client_app():
  return app.send_static_file('app.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)