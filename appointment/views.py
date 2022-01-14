# File that includes the functions of appointment
# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
import datetime
from datetime import time
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
@requires_roles('doctor', 'patient')
@login_required
def appointment():
    if current_user.role == 'patient':
        return render_template('appointments.html',
                               appointments=Appointment.query.filter_by(patient_id=current_user.id)
                               .order_by(Appointment.date.asc(), Appointment.time.asc()),
                               doctors=User.query.filter_by(role='doctor'),
                               hospitals=Hospital.query.all())
    elif current_user.role == 'doctor':
        return render_template('appointments.html',
                               appointments=Appointment.query.filter_by(doctor_id=current_user.id)
                               .order_by(Appointment.date.asc(), Appointment.time.asc()),
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
    # Time of appointment
    booking_time = request.form.get('book')

    if form.validate_on_submit():
        # Get all appointments in the current date
        apt = Appointment.query.filter_by(date=form.date.data).all()
        # if time found is in
        for apt in apt:
            if apt.site_id == site.id:
                if apt.time in times:
                    times.remove(apt.time)

        # if no slots remain in the list
        if not times:
            flash('Current date is fully booked')
        # If n isnt none, so the time the book button is pressed
        if booking_time:
            # Create new appointment and add it to the database
            booking_time = datetime.datetime.strptime(booking_time, '%H:%M:%S')
            booking_time = booking_time.time()
            new_appointment = Appointment(current_user.id, findDoctor(form.date.data, booking_time).id,
                                          form.date.data, booking_time, notes='pending', site_id=site.id)
            db.session.add(new_appointment)
            db.session.commit()

            # After booking an appointment redirect to view appointment page
            return redirect(url_for('appointment.appointment'))
        return render_template('book.html', form=form, hospitals=hospitals, slotList=True, timeslots=times)

    # if request method is GET or form not valid re-render booking page
    return render_template('book.html', form=form, hospitals=hospitals, slotList=False, timeslots=times)


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
    # Value to hold least amount of appointments
    min_appointments = -1
    index = 0
    # Get all doctors from the database
    doctors = User.query.filter_by(role='doctor').all()
    # check all doctors
    for doctor in doctors:
        # get all appointments for specific doctor for specific time and date
        appointments = Appointment.query.filter_by(doctor_id=doctor.id, date=date, time=time).all()
        # Loop through all appointments
        for apt in range(len(appointments)):
            # if min appointments is -1 set it to first doctor
            if min_appointments == -1:
                min_appointments = len(appointments)
                index = apt

            # if
            elif len(appointments) < min_appointments:
                min_appointments = len(appointments)
        # if appointments is empty means that no such appointment was found
        if not appointments:
            return doctor
