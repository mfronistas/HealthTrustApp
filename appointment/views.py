# File that includes the functions of appointment
# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
import datetime, time
from app import db, requires_roles
from flask_login import login_required, current_user
from models import Appointment, User, Hospital
# CONFIG
from users.forms import AppointmentForm

appointment_blueprint = Blueprint('appointment', __name__, template_folder='templates')


# VIEWS
# View appointment page

# Might not be needed
@appointment_blueprint.route('/appointment')
@login_required
def appointment():
    return render_template('appointments.html',
                           appointments=Appointment.query.filter_by(patient_id=current_user.id),
                           doctors=User.query.filter_by(role='doctor'),
                           hospitals=Hospital.query.all())


@appointment_blueprint.route('/book_appointment', methods=['POST', 'GET'])
@login_required
def book_appointment():
    # Get all hospitals from database to add them to dropdown list in html page
    hospitals = Hospital.query.all()
    times = timeslots()
    # create appointment form object
    form = AppointmentForm()
    x = request.form.get('location')
    site = Hospital.query.filter_by(name=x).first()
    # if request method is POST or form is valid
    if form.validate_on_submit():
        # Get all appointments in the current date
        print(x)
        print("form is valid")
        appointment = Appointment.query.filter_by(date=form.date.data).all()
        # if time found is in
        # TODO: Check for hospitals
        for i in appointment:
            if i.time in times:
                times.remove(i.time)

        # if no slots remain in the list
        if not times:
            flash('Current date is fully booked')
            return render_template('book.html', form=form, hospitals=hospitals, slotList=False, timeslots=times)
        return render_template('book.html', form=form, hospitals=hospitals, slotList=True, timeslots=times)

    # if request method is GET or form not valid re-render booking page
    return render_template('book.html', form=form, hospitals=hospitals, slotList=False, timeslots=times)

# TODO: Create a method to create a new appointment

# Method to create timeslots and add them to a list
def timeslots() -> list:
    start_time = '9:00'
    end_time = '18:00'
    slot_time = 15

    slots = []
    # Create timeslots
    time = datetime.datetime.strptime(start_time, '%H:%M')
    end = datetime.datetime.strptime(end_time, '%H:%M')
    while time <= end:
        slots.append(time.time())
        time += datetime.timedelta(minutes=slot_time)

    return slots


# Method to find available doctor and assign him to appointment
def findDoctor(date, time) -> User:
    # Get all doctors from the database
    doctors = User.query.filter_by(role='doctor').all()
    # check all doctors
    for doctor in doctors:
        # get all appointments for specific doctor for specific time and date
        appointments = Appointment.query.filter_by(doctor_id=doctor.id, date= date, time=time)
        # if appointments is empty means that no such appointment was found
        if not appointments:
            return doctor



