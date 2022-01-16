# IMPORTS
from datetime import datetime, date, time
from flask_login import UserMixin
from sqlalchemy import ForeignKey, MetaData
from sqlalchemy import Column, Integer, String
from app import db
from werkzeug.security import generate_password_hash
import base64
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet


# Function to encrypt data
def encrypt(data, encryption_key):
    return Fernet(encryption_key).encrypt(bytes(data, 'utf-8'))


# Function that generates encryption key
def generate_key():
    key = Fernet.generate_key()
    return key


# Function to decrypt data
def decrypt(data, encryption_key):
    return Fernet(encryption_key).decrypt(data).decode('utf-8')


# Class User
class User(db.Model, UserMixin):
    __tablename__ = 'User'

    # User information
    id = Column(db.Integer, primary_key=True)
    firstname = Column(db.String(100), nullable=False)
    lastname = Column(db.String(100), nullable=False)
    gender = Column(db.String(100), nullable=False)
    birthdate = Column(db.Date, nullable=False)
    role = Column(db.String(100), nullable=False, default='patient')
    nhs_number = Column(db.Integer, nullable=True)
    phone = Column(db.Integer, nullable=False)

    # User address
    street = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)

    # User auth information
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    encryption_key = db.Column(db.String(100), nullable=False)

    # User activity
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)

    # User constructor
    def __init__(self, firstname, lastname, gender, birthdate, role, nhs_number, phone, street, postcode, city, email,
                 password, encryption_key):
        self.firstname = firstname
        self.lastname = lastname
        self.gender = gender
        self.birthdate = birthdate
        self.role = role
        self.nhs_number = nhs_number
        self.phone = phone
        self.street = street
        self.postcode = postcode
        self.city = city
        self.email = email
        # Generating password hash
        self.password = generate_password_hash(password)
        self.encryption_key = encryption_key
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None


# Class Hospital
class Hospital(db.Model):
    __tablename__ = 'Hospital'

    # Hospital info
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Hospital address
    street = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)

    # Hospital constructor
    def __init__(self, name, street, postcode, city):
        self.name = name
        self.street = street
        self.postcode = postcode
        self.city = city


# Class Appointment
class Appointment(db.Model):
    __tablename__ = 'Appointment'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, ForeignKey('User.id'), nullable=False)
    doctor_id = db.Column(db.Integer, ForeignKey('User.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.String(200))
    site_id = db.Column(db.Integer, ForeignKey('Hospital.id'), nullable=False)

    # Appointment constructor
    def __init__(self, patient_id, doctor_id, date, time, notes, site_id):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.time = time
        self.notes = notes
        self.site_id = site_id


# Class Medicine
class Medicine(db.Model):
    __tablename__ = 'Medicine'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # long term or short term
    dosage = db.Column(db.String(100), nullable=False)

    # Medicine constructor
    def __init__(self, name, type, dosage):
        self.name = name
        self.type = type
        self.dosage = dosage


# Class Prescription
class Prescription(db.Model):
    __tablename__ = 'Prescription'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, ForeignKey('Medicine.id'), nullable=False)
    appointment_id = db.Column(db.Integer, ForeignKey('Appointment.id'), nullable=False)
    instructions = db.Column(db.String(100), nullable=False)

    def __init__(self, medicine_id, appointment_id, instructions):
        self.medicine_id = medicine_id
        self.appointment_id = appointment_id
        self.instructions = instructions


# Database initialization script
def init_db():
    db.drop_all()
    db.create_all()
    patient = User(firstname='John', lastname='Smith', gender='male', birthdate=datetime(1999,5,9), role='patient',
                   nhs_number='1234567891', phone='6909876712', email='jsmith@email.com', password='123123',
                   encryption_key=generate_key(), street='Hawkhill 15', postcode='NE51ER', city='Newcastle')
    doctor = User(firstname='Mathew', lastname='Anderson', gender='Male', birthdate=datetime(1998,3,4), role='doctor',
                  nhs_number=None, phone='8909887890', email='manderson@hospital.com', password='77887788',
                  encryption_key=generate_key(), street='North 29', postcode='NE78RE', city='Newcastle')
    admin = User(firstname='Alice', lastname='Smith', gender='Female', birthdate=datetime(1999, 5, 4), role='admin',
                 nhs_number=None, phone='8909887891', email='admin@email.com', password='123123',
                 encryption_key=generate_key(), street='South 29', postcode='NE24DF', city='Newcastle')
    hospital = Hospital(name='General Hospital', street='South 23', postcode='NE24DF', city='Newcastle')
    hospital2 = Hospital(name='Victoria Hospital', street='North 40', postcode='NE25DF', city='Newcastle')
    medicine = Medicine(name='PainkillerOmega', type='painkiller', dosage=30)
    db.session.add(patient)
    db.session.add(doctor)
    db.session.add(admin)
    db.session.add(hospital)
    db.session.add(hospital2)
    db.session.add(medicine)
    db.session.commit()

def create_appointment():
    appointment = Appointment(patient_id=1, doctor_id=2, date=date(2022, 1, 15), time=time(9, 00), notes="", site_id=2)
    db.session.add(appointment)
    db.session.commit()
