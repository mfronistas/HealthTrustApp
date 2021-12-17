# File that includes the functions of appointment
# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from app import db, requires_roles
from flask_login import login_required, current_user
from models import Appointment
# CONFIG
from users.forms import AppointmentForm

appointment_blueprint = Blueprint('appointment', __name__, template_folder='templates')


# VIEWS
# View appointment page

# Might not be needed
@appointment_blueprint.route('/appointment')
@login_required
def appointment():
    return render_template('book.html')


@appointment_blueprint.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    form = AppointmentForm
    if current_user.role == 'patient':
        new_appointment = Appointment(patient_id=current_user.id, doctor_id=form.doctor.data, date=form.date.data,
                                      time=form.time.data, notes=form.notes.data, site_id=form.site.data)

        # add appointment to database
        db.session.add(new_appointment)
        db.session.commit()
        # TODO Create template view appointments or route page where user can see appointments
        return render_template(url_for('view_appointments.html'))

    # TODO complete receptionist booking
    if current_user.role == 'reception':
        new_appointment = Appointment(patient_id=form.patient.data, doctor_id=form.doctor.data, date=form.date.data,
                                      time=form.time.data, notes=form.notes.data, site_id=form.site.data)

        # add appointment to database
        db.session.add(new_appointment)
        db.session.commit()
        # TODO Create template view appointments or route page where user can see appointments
        return render_template(url_for('view_appointments.html'))
