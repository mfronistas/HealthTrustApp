"""Module that contains all functions for admin"""
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from flask_mail import Message
from app import db, requires_roles, mail
from models import User, Medicine, Hospital
from users.forms import DoctorForm, MedicineForm, HospitalForm

# CONFIG
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


# ROUTES
# Main page for admin
@admin_blueprint.route('/admin')
@login_required
@requires_roles('admin')
def admin():
    """Method to return the home page for admin with the last 10 log entries"""
    with open("healthtrust.log", "r") as file:
        content = file.read().splitlines()[-10:]
        content.reverse()

    return render_template('adminhome.html', logs=content)


# Page to view all doctors
@admin_blueprint.route('/view_all_doctors', methods=['POST', 'GET'])
@login_required
@requires_roles('admin')
def view_all_doctors():
    """Method to view all doctors for admin"""

    cancel = request.form.get('valuecancel')

    if cancel:
        try:
            User.query.filter_by(id=cancel).delete()
            db.session.commit()
            return redirect(url_for('admin.view_all_doctors'))
        except:
            raise Exception('Doctor not in database')
    return render_template('adddoctor.html', doctors=User.query.filter_by(role='doctor').all())


@admin_blueprint.route('/add_doctor', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_doctor():
    """Method to add a new doctor for admin"""
    # create signup form object
    form = DoctorForm()
    # if request method is POST or form is valid
    if form.validate_on_submit():
        doc = User.query.filter_by(email=form.email.data).first()
        # if email already exists redirect user back to signup page
        if doc:
            flash('Email address already exists', 'error')
            return render_template('adddoctor.html', form=form)

        new_doctor = User(firstname=form.firstname.data,
                          lastname=form.lastname.data,
                          gender=form.gender.data,
                          birthdate=form.birthdate.data,
                          role='doctor',
                          nhs_number=None,
                          phone=form.phone.data,
                          street=form.street.data,
                          postcode=form.postcode.data,
                          city=form.city.data,
                          email=form.email.data,
                          password=form.password.data)
        db.session.add(new_doctor)
        db.session.commit()
        # Send email to new user created to set up 2 factor authenticator
        msg = Message(subject='Activate 2 Factor Authentication',
                      sender='healthtrust.contact@gmail.com',
                      recipients=[new_doctor.email])
        msg.body = 'PIN Key: {pinkey}\n\n' \
                   'For Doctor Account: {email}\n\n' \
                   '--Set up One Time Password generator--\n\n' \
                   '1) Download Authy on your device, https://authy.com/download/\n\n' \
                   '2) Select add new account\n\n' \
                   '3) Enter your PIN key\n\n' \
                   '4) Enter name for new account\n\n' \
                   '5) Select token length of 6\n\n' \
                   '6) Use the generated codes to log in your account' \
            .format(email=new_doctor.email, pinkey=new_doctor.encryption_key)
        mail.send(msg)

        return redirect(url_for('admin.view_all_doctors'))
    return render_template('adddoctor.html', form=form, add_doc=True)


# Method to view all medicines
@admin_blueprint.route('/view_all_medicine', methods=['POST', 'GET'])
@login_required
@requires_roles('admin')
def view_all_medicine():
    """Method to view all medicines for admin"""
    cancel = request.form.get('valuecancel')

    if cancel:
        try:
            Medicine.query.filter_by(id=cancel).delete()
            db.session.commit()
            return redirect(url_for('admin.view_all_medicine'))
        except:
            raise Exception('Medicine not in database')
    return render_template('addmed.html', cur_med=Medicine.query.all())


# Method to add a new medicine to database
@admin_blueprint.route('/add_medicine', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_medicine():
    """Method to add a new medicine for admin"""
    # create signup form object
    form = MedicineForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        med = Medicine.query.filter_by(name=form.name.data).first()

        if med:
            flash('Medicine already exists', 'error')
            return render_template('addmed.html', form=form)

        new_med = Medicine(name=form.name.data,
                           type=form.type.data,
                           dosage=form.dosage.data)
        db.session.add(new_med)
        db.session.commit()
        return redirect(url_for('admin.view_all_medicine'))
    return render_template('addmed.html', form=form, add_med=True)


# Method to view all hospitals
@admin_blueprint.route('/view_all_hospitals', methods=['POST', 'GET'])
@login_required
@requires_roles('admin')
def view_all_hospitals():
    """Method to view all hospitals for admin"""
    cancel = request.form.get('valuecancel')

    if cancel:
        try:
            Hospital.query.filter_by(id=cancel).delete()
            db.session.commit()
            return redirect(url_for('admin.view_all_hospitals'))
        except:
            raise Exception('Hospital not in database')
    return render_template('addhospital.html', cur_hospital=Hospital.query.all())


# Method to add a new hospital to database
@admin_blueprint.route('/add_hospital', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_hospital():
    """Method to add a new hospital for admin"""
    # create signup form object
    form = HospitalForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        hospital = Hospital.query.filter_by(name=form.name.data).first()

        if hospital:
            flash('Hospital already exists', 'error')
            return render_template('addhospital.html', form=form)

        new_hospital = Hospital(name=form.name.data,
                                city=form.city.data,
                                street=form.street.data,
                                postcode=form.postcode.data,)
        db.session.add(new_hospital)
        db.session.commit()
        return redirect(url_for('admin.view_all_hospitals'))
    return render_template('addhospital.html', form=form, add_hos=True)
