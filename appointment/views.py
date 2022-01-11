# File that includes the functions of appointment
# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
import datetime
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
    # create appointment form object
    form = AppointmentForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        # Get all appointments in the current date
        times = timeslots()
        appointment = Appointment.query.filter_by(date=form.date.data)
        # if time found is in
        for i in appointment:
            if i.time in times:
                times.remove(i)

        # if no slots remain in the list
        if times == '':
            flash('Current date is fully booked')
            return render_template('book.html', form=form)

        # if entered time not in times remaining, means that the time is already booked
        if form.time.data not in times:

            # if user is patient use his current id to book appointment
            if current_user.role == 'patient':
                new_appointment = Appointment(patient_id=current_user.id, doctor_id=form.doctor.data, date=form.date.data,
                                              time=form.time.data, notes=form.notes.data, site_id=form.site.data)

                # add appointment to database
                db.session.add(new_appointment)
                db.session.commit()
                return render_template(url_for('book.html'))

            # If user is a receptionist choose a user from the list to get his id
            if current_user.role == 'reception':
                new_appointment = Appointment(patient_id=form.patient.data, doctor_id=form.doctor.data, date=form.date.data,
                                              time=form.time.data, notes=form.notes.data, site_id=form.site.data)

                # add appointment to database
                db.session.add(new_appointment)
                db.session.commit()
                return render_template(url_for('book.html'))
        else:
            flash('Time already booked')
    # if request method is GET or form not valid re-render booking page
    return render_template('book.html', form=form)


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
        slots.append(time.strftime("%H:%M"))
        time += datetime.timedelta(minutes=slot_time)

    return slots
