from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(engine_options={"pool_pre_ping":True})
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

### comeback and update toDict methods to include relationships

class User(UserMixin, db.Model):
    __tablename__='user'
  
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), nullable=False)
    email=db.Column(db.String(50), nullable=False, unique=True)
    password=db.Column(db.String(80), nullable=False)
    date_of_birth=db.Column(db.Date, nullable=False)
    address=db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)    
    num_visits = db.Column(db.Integer, default=0)
    img = db.Column(db.String(60), nullable=False)
    
    
    

    __mapper_args__ = {        
        'polymorphic_on':type,
        'polymorphic_identity':'user'
    }


    def toDict(self):
        return{            
            'fname': self.fname,
            'lname': self.lname,   
            'email': self.email,         
            'password': self.password,            
            'date_of_birth': self.date_of_birth.strftime("%d-%B-%Y"),
            'address': self.address,
            'type': self.type,
            'num_visits': self.num_visits
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.fname+" "+self.lname)

    ##finish authentication




class Patient(User):
    ##__tablename__='patient'

    
    med_record = db.relationship('Med_Record', uselist=False, backref='patient')
    releases = db.relationship('Release_Form', foreign_keys="Release_Form.patient_id", backref='patient', lazy=True)    
    appointments = db.relationship('Appointment', foreign_keys="Appointment.patient_id", backref='patient', lazy=True)
        
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
    #license = db.Column(db.String(20), nullable=False)
    med_id=db.Column(db.Integer, db.ForeignKey('med_institution.id'))
    releases=db.relationship('Release_Form', foreign_keys="Release_Form.physician_id", backref='physician', lazy=True)    
    appointments = db.relationship('Appointment', foreign_keys="Appointment.physician_id", backref='physician', lazy=True)##, back_populates="physicians")
    


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
    id = db.Column(db.Integer, primary_key=True)
    physician_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    date=db.Column(db.DateTime, default=datetime.datetime.utcnow())    
    
    def toDict(self):
        return {
            'date': self.date.strftime("%d-%B-%Y %H:%M:%S") 
        }
 

class Med_Institution(db.Model):
    __tablename__='med_institution'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    contact_no = db.Column(db.String(15), nullable=False)    
    physician = db.relationship('Physician', backref='med_institution', lazy=True)


    def toDict(self):
        return{
            'id':self.id,
            'address':self.address,
            'name':self.name,
            'contact_no': self.contact_no   
        }
               

class Med_Record(db.Model):
    __tablename__='med_record'

    id = db.Column(db.Integer, primary_key=True)    
    current_problem = db.Column(db.String(50), nullable=True)
    current_treatment=db.Column(db.String(50), nullable=True)
    history=db.Column(db.String(5000), nullable=True)
    patient_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


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
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False) ##foreign key
    physician_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
     

    def toDict(self):
        return {
            'id':self.id,
            'date': self.date.strftime("%d-%B-%Y %H:%M:%S")         
        }

