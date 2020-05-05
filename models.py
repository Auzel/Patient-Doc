from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

### comeback and update toDict methods to include relationships

class User(UserMixin, db.Model):
    __tablename__='user'

    username=db.Column(db.String(20), nullable=False, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    password=db.Column(db.String(80), nullable=False)
    date_of_birth=db.Column(db.Date, nullable=False)
    address=db.Column(db.String(50), nullable=False)
    email= db.Column(db.String(50), nullable=False, unique=True)
    
    type = db.Column(db.String(50))

    __mapper_args__ = {        
        'polymorphic_on':type,
        'polymorphic_identity':'user'
    }


    def toDict(self):
        return{
            'username': self.username,
            'fname': self.fname,
            'lname': self.lname,            
            'password': self.password,            
            'date_of_birth': self.date_of_birth.strftime("%d/%B/%Y"),
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
    
    def get_id(self):
        return self.username

    ##finish authentication




class Patient(User):
    ##__tablename__='patient'

    
    med_record = db.relationship('Med_Record', uselist=False, backref='patient')
    releases = db.relationship('Release_Form', foreign_keys="Release_Form.patient_username",  lazy=True)    
    appointments = db.relationship('Appointment', foreign_keys="Appointment.patient_username", backref='patient', lazy=True)
        
    __mapper_args__ = {
        'polymorphic_identity':'patient'
    }


    def toDict(self):
        return super().toDict()
        
class Physician(User):
    ##__tablename__='physician'

    type1= db.Column(db.String(20), nullable=False)
    degree=db.Column(db.String(20), nullable=False)
    place_of_education=db.Column(db.String(20), nullable=False)
    med_id=db.Column(db.Integer, db.ForeignKey('med_institution.id'))
    releases=db.relationship('Release_Form', foreign_keys="Release_Form.physician_username", backref='physician', lazy=True)    
    appointments = db.relationship('Appointment', foreign_keys="Appointment.physician_username", backref='physician', lazy=True)##, back_populates="physicians")
    
    __mapper_args__ = {
        'polymorphic_identity':'physician'
    }

    ##appointment date scheduling

    def toDict(self):
        return  super().toDict().update({
                'type1':self.type1,
                'degree':self.degree,
                'place_of_education':self.place_of_education
            })   


class Appointment(db.Model):
    physician_username = db.Column(db.String(20), db.ForeignKey('user.username'), primary_key=True)
    patient_username = db.Column(db.String(20), db.ForeignKey('user.username'), primary_key=True) 
    date=db.Column(db.DateTime, primary_key=True, default=datetime.datetime.utcnow())    
    
    def toDict(self):
        return {
            'date': self.date.strftime("%d/%B/%Y, %H:%M:%S") 
        }
 

class Med_Institution(db.Model):
    __tablename__='med_institution'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    physician = db.relationship('Physician', backref='med_institution', lazy=True)

    def toDict(self):
        return{
            'id':self.id,
            'address':self.address,
            'name':self.name
        }
               

class Med_Record(db.Model):
    __tablename__='med_record'

    id = db.Column(db.Integer, primary_key=True)    
    current_problem = db.Column(db.String(20), nullable=True)
    current_treatment=db.Column(db.String(20), nullable=True)
    history=db.Column(db.String(1000), nullable=True)
    patient_username=db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)


    def toDict(self):
        return{
            'id':self.id,
            'history':self.history,
            'current_problem':self.current_problem,
            'current_treatment':self.current_treatment
        }
    
class Release_Form(db.Model):
    __tablename__='release_form'

    id = db.Column(db.Integer, primary_key=True) 
    date=db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())   
    patient_username = db.Column(db.String(20), db.ForeignKey('user.username'),nullable=False) ##foreign key
    physician_username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
     

    def toDict(self):
        return {
            'id':self.id,
            'date': self.date.strftime("%d/%B/%Y, %H:%M:%S")         
        }