from main import app
from models import db

db.create_all(app=app)

#put med institutions
#some doctors
#some patients

print('database initialized!')