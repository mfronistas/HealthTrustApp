"""This module contain all models for database tables,
pinkey generation method and initialization of the database"""
# IMPORTS
from datetime import datetime, date, time

import pyotp
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy import Column
from app import db
from werkzeug.security import generate_password_hash


# Function that generates encryption key
def generate_pinkey():
    """Method to generate pinkey needed in two-factor authorisation

    :return key -- a unique pinkey
    """
    key = pyotp.random_base32()
    return key


# Class User
class User(db.Model, UserMixin):
    """A model for the User table

    id -- the id that the User is assigned to in the database
    firstname -- the firstname of the User
    lastname -- the lastname of the User
    gender -- the gender the User identifies with
    birthdate -- the date when the User has been born
    role -- the role and permissions assigned to the User. Set to 'patient' by default
    nhs_number  -- the NHS number of the User
    phone -- the phone number of the User
    street -- the street the User lives on
    postcode -- the postcode of the place the User lives in
    city -- the city where the User lives
    email -- the email address of the User
    password -- the password to access the account
    encryption_key -- the key assigned to the User account that is used to generate the pinkey
    registered_on -- the date when the account was registered
    last_logged_in -- the date when the User's account was last accessed successfully
    current_logged_in -- the date when the most recent successful logging in happened

    """
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
                 password):
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
        self.encryption_key = generate_pinkey()
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None


# Class Hospital
class Hospital(db.Model):
    """A model for the Hospital table

    id -- the id that the Hospital is assigned to in the database
    name -- the name of the Hospital
    street -- the street where the Hospital is
    postcode -- the postcode of the place where the Hospital is
    city -- the city the Hospital is in

    """
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
    """A model for the Appointment table

    id -- the id the Appointment is assigned to in the database
    patient_id -- the patient that has booked the Appointment
    doctor_id -- the doctor that will run the Appointment
    date -- the date of the Appointment
    time -- the time of the Appointment
    notes -- the notes about the Appointment
    site_id -- the Hospital where the Appointment takes place

    """
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
    """A model for the Medicine table

    id -- the id that the Medicine is assigned to in the database
    name -- the name of the Medicine
    type -- the type of the Medicine
    dosage -- the dosage that the Medicine have

    """
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
    """A model for the Prescription table

    id -- the id that the Perscription is assigned to in the database
    medicine_id -- the id of the Medicine used in the Prescription
    appointment_id -- the id of the Appointment where the Prescription was made
    instruction -- the instructions on the Prescription made by doctor on how to use the Medicine

    """
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
    """Initialization of the database tables and initial entries
    """
    db.drop_all()
    db.create_all()
    patient = User(firstname='John', lastname='Smith', gender='male', birthdate=datetime(1999, 5, 9), role='patient',
                   nhs_number='1234567891', phone='6909876712', email='jsmith@email.com', password='123123',
                   street='Hawkhill 15', postcode='NE51ER', city='Newcastle')
    doctor = User(firstname='Mathew', lastname='Anderson', gender='Male', birthdate=datetime(1998, 3, 4), role='doctor',
                  nhs_number=None, phone='8909887890', email='manderson@hospital.com', password='77887788',
                  street='North 29', postcode='NE78RE', city='Newcastle')
    admin = User(firstname='Alice', lastname='Smith', gender='Female', birthdate=datetime(1999, 5, 4), role='admin',
                 nhs_number=None, phone='8909887891', email='admin@email.com', password='123123',
                 street='South 29', postcode='NE24DF', city='Newcastle')
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


# Function to create an appointment.
def create_appointment():
    """Manual appointment creation"""
    appointment = Appointment(patient_id=1, doctor_id=2, date=date(2022, 1, 15), time=time(9, 00), notes="", site_id=2)
    db.session.add(appointment)
    db.session.commit()
