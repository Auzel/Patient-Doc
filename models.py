from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

### comeback and update toDict methods
class Med_Institution:

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    ##physician = db.relationship('Physician', backref='med_institution', lazy=True)

    def toDict(self):
        return{
            'id':self.id,
            'address':self.address,
            'name':self.name
        }
        


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fName = db.Column(db.String(20), nullable=False)
    lName = db.Column(db.String(20), nullable=False)
    username=db.Column(db.String(20), nullable=False)
    password=db.Column(db.String(20), nullable=False)
    date_of_birth=db.Column(db.DateTime, nullable=False)
    address=db.Column(db.String(50), nullable=False)
    

    def toDict(self):
        return{
            'id': self.id,
            'fName': self.fName,
            'lName': self.lName,
            'username': self.username,
            'password': self.password,            
            'date_of_birth': self.date_of_birth.strftime("%m/%d/%Y, %H:%M:%S"),
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


'''physicians=db.Table('physicians',db.Column('physician_id', db.Integer, db.ForeignKey('physician.id'), primary_key=True), db.Column('patient_id', db.Integer, db.ForeignKey('patient.id'), primary_key=True)) '''


class Physician(User):
    type1= db.Column(db.String(20), nullable=False)
    degree=db.Column(db.String(20), nullable=False)
    place_of_education=db.Column(db.String(20), nullable=False)
  ##  med_id=db.Column(db.Integer, db.ForeignKey('med_institution.id'), nullable=False)
  ##  releases=db.relationship('Release_Form', backref='physician', lazy=True)

    ##appointment date scheduling

    def toDict(self):
        return{
            self().toDict().update({
                'type1':self.type1,
                'degree':self.degree,
                'place_of_education':self.place_of_education
            })   
        }

class Patient(User):
    current_problem = db.Column(db.String(20), nullable=True)
    current_treatment=db.Column(db.String(20), nullable=True)
  ##  med_History = db.relationship('Med_History', uselist=False)
  ##  releases = db.relationship('Release_Form', lazy=True)
  ##  physicians=db.relationship('Physician', secondary=physicians, lazy='subquery', backref=db.backref('patients', lazy=True))


    def toDict(self):
        return{
            self().toDict().update({
                'current_problem':self.current_problem,
                'current_treatment':self.current_treatment
            })   
        }

class MedHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    description=db.Column(db.String(1000), nullable=True)
  ##  patient_id=db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    ##create new table for separate allergies since 

    def toDict(self):
        return{
            'id':self.id,
            'description':self.description   
        }
    
class ReleaseForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
  ##  patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'),nullable=False) ##foreign key
  ##  physician_id = db.Column(db.Integer, db.ForeignKey('physician.id'), nullable=False)
     

    def toDict(self):
        return {
            'id':self.id            
        }