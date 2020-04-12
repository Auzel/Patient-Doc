from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


class MedInstitution:
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fName = db.Column(db.String(20), nullable=False)
    lName = db.Column(db.String(20), nullable=False)
    username=db.Column(db.String(20), nullable=False)
    password=db.Column(db.String(20), nullable=False)
    dateOfBirth=db.Column(db.DateTime, default=datetime.datetime.utcnow)
    address=db.Column(db.String(50), nullable=False)

    def toDict(self):
        return{
            'id': self.id,
            'fName': self.fName,
            'lName': self.lName,
            'username': self.username,
            'password': self.password,            
            'dateOfBirth': self.created.strftime("%m/%d/%Y, %H:%M:%S"),
            'address': self.address
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    ##finish authentication


class Physician(User):
    type1= db.Column(db.String(20), nullable=False)
    degree=db.Column(db.String(20), nullable=False)
    placeOfEducation=db.Column(db.String(20), nullable=False)
    ##appointment date scheduling

    def toDict(self):
        return{
            self().toDict().update({
                'type1':self.type1,
                'degree':self.degree,
                'placeOfEducation':self.placeOfEducation
            })   
        }

class Patient(User):
    currentProblem = db.Column(db.String(20), nullable=False)
    currentTreatment=db.Column(db.String(20), nullable=False)

    def toDict(self):
        return{
            self().toDict().update({
                'currentProblem':self.currentProblem,
                'currentTreatment':self.currentTreatment,
                'placeOfEducation':self.placeOfEducation
            })   
        }

class MedHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    description=db.Column(db.String(1000), nullable=False)
    ##create new table for separate allergies since 

    def toDict(self):
        return{
            'id':self.id,
            'description':self.description   
        }
    
