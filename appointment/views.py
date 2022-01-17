# File that includes the functions of appointment
# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
import datetime
from datetime import time
from flask_mail import Mail, Message
from app import db, requires_roles, mail
from flask_login import login_required, current_user
from models import Appointment, User, Hospital, Medicine, Prescription
# CONFIG
from users.forms import AppointmentForm, PrescriptionForm

appointment_blueprint = Blueprint('appointment', __name__, template_folder='templates')


# VIEWS
# View appointment page
@appointment_blueprint.route('/appointment', methods=['POST', 'GET'])
@requires_roles('doctor', 'patient')
@login_required
def appointment():

    cancel = request.form.get('valuecancel')

    if current_user.role == 'patient':

        if cancel:
            try:
                Appointment.query.filter_by(id=cancel).delete()
                db.session.commit()
                flash('Appointment canceled')
                return redirect(url_for('appointment.appointment'))

            except:
                raise Exception('Appointment not in database')

        return render_template('appointments.html',
                               appointments=Appointment.query.filter_by(patient_id=current_user.id)
                               .order_by(Appointment.date.asc(), Appointment.time.asc()),
                               doctors=User.query.filter_by(role='doctor'),
                               hospitals=Hospital.query.all())
    elif current_user.role == 'doctor':
        if cancel:

            appointment = Appointment.query.filter_by(id=cancel).first()
            user = User.query.filter_by(id=appointment.patient_id).first()
            email = user.email
            date = appointment.date
            doctor = User.query.filter_by(id=appointment.doctor_id).first()
            phone = doctor.phone

            try:
                msg = Message(subject='Health Trust Appointment Canceled', sender='healthtrust.contact@gmail.com',
                              recipients=[email])
                msg.body = 'Appointment Date: {date}  \n' \
                           'Canceled by the doctor\n' \
                           'Please contact Dr.{doctor} using this number {phone}'.format(date=date,
                                                                                      doctor=doctor.lastname,
                                                                                      phone=phone)
                mail.send(msg)
                Appointment.query.filter_by(id=cancel).delete()
                db.session.commit()
                flash('Appointment canceled')

                return redirect(url_for('appointment.appointment'))

            except:
                raise Exception('Appointment not in database')

        return render_template('appointments.html',
                               appointments=Appointment.query.filter_by(doctor_id=current_user.id)
                               .order_by(Appointment.date.asc(), Appointment.time.asc()),
                               patients=User.query.filter_by(role='patient'),
                               hospitals=Hospital.query.all())



@appointment_blueprint.route('/book_appointment', methods=['POST', 'GET'])
@login_required
@requires_roles('patient', 'doctor')
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
            flash('Current date is fully booked', 'error')
            return render_template('book.html', form=form, hospitals=hospitals, slotList=False, timeslots=times)

        # If user has booked another appointment for the same date
        if Appointment.query.filter_by(patient_id=current_user.id, date=form.date.data).first():
            flash('Appointment already booked for specific date')
            return render_template('book.html', form=form, hospitals=hospitals, slotList=False, timeslots=times)
        # If n isnt none, so the time the book button is pressed
        if booking_time:
            # Create new appointment and add it to the database
            booking_time = datetime.datetime.strptime(booking_time, '%H:%M:%S')
            booking_time = booking_time.time()
            new_appointment = Appointment(current_user.id, findDoctor(form.date.data, booking_time).id,
                                          form.date.data, booking_time, notes='pending', site_id=site.id)
            db.session.add(new_appointment)
            db.session.commit()
            flash('Appointment Booked!')

            # After booking an appointment redirect to view appointment page
            return redirect(url_for('appointment.appointment'))
        return render_template('book.html', form=form, hospitals=hospitals, slotList=True, timeslots=times)

    # if request method is GET or form not valid re-render booking page
    return render_template('book.html', form=form, hospitals=hospitals, slotList=False, timeslots=times)


@appointment_blueprint.route('/appointmentview', methods=['POST', 'GET'])
@login_required
def view_appointment():
    form = PrescriptionForm()
    date = request.form.get("view-date")
    appointment_time = request.form.get("view-time")
    appointment_id = request.form.get("view")
    patient = request.form.get("view-patient")
    doctor = request.form.get("view-doctor")
    hospital = request.form.get("view-hospital")
    patient_id = request.form.get("view-id")
    patient_data = User.query.filter_by(id=patient_id).first()
    medicines = Medicine.query.all()
    medicine = request.form.get('medicine')
    prescriptions = Prescription.query.filter_by(appointment_id=appointment_id).all()
    if form.validate_on_submit():
        new_prescription = Prescription(medicine_id=medicine, appointment_id=appointment_id,
                                        instructions=form.instructions.data)
        db.session.add(new_prescription)
        db.session.commit()
    return render_template('appointmentview.html', date=date, time=appointment_time, prescriptions=prescriptions,
                           patient=patient, doctor=doctor, hospital=hospital, patient_data=patient_data,
                           medicine=medicines, form=form, patient_id=patient_id, appointment_id=appointment_id)


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
    # Variable to hold lowest appointment doctor
    index = 0
    # Get all doctors from the database
    doctors = User.query.filter_by(role='doctor').all()
    # check all doctors
    for doctor in doctors:
        # get all appointments for specific doctor for specific date
        appointments = Appointment.query.filter_by(doctor_id=doctor.id, date=date).all()

        # if min appointments is -1 set it to first doctor
        if min_appointments == -1:
            min_appointments = len(appointments)

        # if length of appointments is less than min_appointments
        if len(appointments) < min_appointments:
            # If doctor doesnt have an appoitnemtn at that time
            if not Appointment.query.filter_by(doctor_id=doctor.id, date=date, time=time).first():
                min_appointments = len(appointments)
                index = doctor

        # if appointments is empty means that no such appointment was found
        if not appointments:
            return doctor
    # Return the lowest appointment doctor
    return index
