"""This module holds all the user functions
for roles patient and doctor"""
# IMPORTS
import logging
from datetime import datetime
from random import randint
from werkzeug.security import check_password_hash, generate_password_hash
import pyotp
from flask_mail import Message
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from app import db, requires_roles, mail
from models import User, Prescription, Appointment, Medicine
from users.forms import RegisterForm, LoginForm, ContactForm, RecoveryForm

# CONFIG

users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """Method to register a new patient"""
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        nhs_num = User.query.filter_by(nhs_number=form.nhs_number.data).first()
        # if this returns a user, then the email or NHS number already exists in database

        # if email or NHS number already exists redirect user
        # back to signup page with error message so user can try again
        if user:
            flash('Email address already exists', 'error')
            return render_template('register.html', form=form)
        if nhs_num:
            flash('This NHS number has already been used', 'error')
            return render_template('register.html', form=form)

        # create a new user with the form data
        new_user = User(firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        gender=form.gender.data,
                        birthdate=form.birthdate.data,
                        role='patient',
                        nhs_number=form.nhs_number.data,
                        phone=form.phone.data,
                        street=form.street.data,
                        postcode=form.postcode.data,
                        city=form.city.data,
                        email=form.email.data,
                        password=form.password.data)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        logging.warning('SECURITY - User registration [%s, %s]', form.email.data,
                        request.remote_addr)

        # Send email to new user created to set up 2 factor authenticator
        msg = Message(subject='Activate 2 Factor Authentication',
                      sender='healthtrust.contact@gmail.com',
                      recipients=[new_user.email])
        msg.body = 'PIN Key: {pinkey}\n\n' \
                   'For Account: {email}\n\n' \
                   '--Set up One Time Password generator--\n\n' \
                   '1) Download Authy on your device, https://authy.com/download/\n\n' \
                   '2) Select add new account\n\n' \
                   '3) Enter your PIN key\n\n' \
                   '4) Enter name for new account\n\n' \
                   '5) Select token length of 6\n\n' \
                   '6) Use the generated codes to log in your account' \
            .format(email=new_user.email, pinkey=new_user.encryption_key)
        mail.send(msg)

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# Login user
@users_blueprint.route('/login', methods=['POST', 'GET'])
def login():
    """Method so all users can log in the application using email, password and pinkey
    in order to access functions depending on their roles,
    failed log in attempts are monitored and if too many user cant log in"""

    # if session attribute logins doesnt exist create new attribute logins
    if not session.get('logins'):
        session['logins'] = 0
    # if login attempts is more than 3 return error message
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded', 'error')

    form = LoginForm()

    if form.validate_on_submit():

        # increase login attempts by 1
        session['logins'] += 1

        user = User.query.filter_by(email=form.email.data).first()
        if not user or not check_password_hash(user.password, form.password.data):
            # if user not authenticated, return error message depending on login attempts
            if session['logins'] == 3:
                flash('Number of incorrect login attempts exceeded', 'error')
                # Security warning for when a user tries to log in 3 times unsuccessfully
                logging.warning('SECURITY - Log in attempt 3[%s, %s]', form.email.data,
                                request.remote_addr)

            elif session['logins'] == 2:
                flash('Please check your login details and try again.'
                      ' 1 login attempt remaining', 'error')
                # Security warning for when a user tries to log in 2 times unsuccessfully
                logging.warning('SECURITY - Log in attempt 2[%s, %s]', form.email.data,
                                request.remote_addr)

            elif session['logins'] == 1:
                flash('Please check your login details and '
                      'try again. 2 login attempt remaining', 'error')
                # Security warning for when a user tries to log in once unsuccessfully
                logging.warning('SECURITY - Log in attempt 1[%s, %s]', form.email.data,
                                request.remote_addr)

            else:
                flash('Please check your login details and try again', 'error')
                # Security warning for when a user tries to log in unsuccessfully
                logging.warning('SECURITY - Log in [%s, %s]', form.email.data,
                                request.remote_addr)

            return render_template('login.html', form=form)

        # If user 2FA is valid
        if pyotp.TOTP(user.encryption_key).verify(form.pin.data):
            # if user is verified reset login attempts
            session['logins'] = 0
            login_user(user)
            # if user logs in, transfer the date and time to last logged in
            user.current_logged_in = datetime.now()
            # Get current datetime for when the user logs in
            user.last_logged_in = user.current_logged_in
            db.session.add(user)
            db.session.commit()
            logging.warning('SECURITY - Log in [%s, %s, %s]', current_user.id, current_user.email,
                            request.remote_addr)
            # Redirect to appropriate page according to role
            if current_user.role == 'admin':
                return redirect(url_for('admin.admin'))
            if current_user.role == 'doctor':
                return redirect(url_for('appointment.appointment'))
            else:
                return redirect(url_for('users.account'))
        # If user enters invalid 2FA code return error
        if not pyotp.TOTP(user.encryption_key).verify(form.pin.data):
            flash('Incorrect Pinkey', 'error')

    return render_template('login.html', form=form)


# Contact us emailing system
@users_blueprint.route('/contactus', methods=['POST', 'GET'])
def contact_us():
    """Method to send an enquiry to the trust
     using the contact us page"""
    # create contact form object
    form = ContactForm()
    # if request method is POST or form is valid
    if form.validate_on_submit():
        # msg is emailed to admin
        msg = Message(subject=form.subject.data, sender='healthtrust.contact@gmail.com',
                      recipients=['healthtrust.contact@gmail.com'])
        msg.body = 'CONTACT US ENQUIRY\n' \
                   'BY: {email}\n' \
                   'Message: {message}'.format(email=form.email.data, message=form.message.data)
        mail.send(msg)
        flash('Message sent!')
        return redirect(url_for('user.contactus'))
    return render_template('contact.html', form=form)


# logout the current user
@users_blueprint.route('/logout')
@login_required
def logout():
    """Method to log out the current user"""
    logging.warning('SECURITY - Log out [%s, %s, %s]',
                    current_user.id, current_user.email, request.remote_addr)
    logout_user()
    return redirect(url_for('index'))


# View prescriptions
@users_blueprint.route('/prescriptions', methods=['POST', 'GET'])
@login_required
@requires_roles('doctor', 'patient')
def view_prescriptions():
    """Method to view prescriptions for patient and doctor,
     doctor is able to delete prescriptions"""
    prescriptions = []
    cancel = request.form.get('valuecancel')
    all_appointments = Appointment.query.all()
    meds = Medicine.query.all()
    patients = User.query.all()
    if current_user.role == 'patient':
        appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
        for appointment in appointments:
            prescription = Prescription.query.filter_by(appointment_id=appointment.id).first()
            if prescription is not None:
                prescriptions.append(prescription)
    elif current_user.role == 'doctor':
        if cancel:
            try:
                Prescription.query.filter_by(id=cancel).delete()
                db.session.commit()
                flash('Prescription canceled')
                return redirect(url_for('users.view_prescriptions'))

            except:
                raise Exception('Prescription not in database')
        appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
        for appointment in appointments:
            prescription = Prescription.query.filter_by(appointment_id=appointment.id).first()
            if prescription is not None:
                prescriptions.append(prescription)

    return render_template('prescriptionview.html', prescriptions=prescriptions,
                           meds=meds, patients=patients,
                           appointments=all_appointments)


# view user account
@users_blueprint.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    """Method to show the user his account information when logging in,
     and also help him update his information"""
    update = request.form.get('update_details')
    if update:
        form = RegisterForm()
        if form.validate_on_submit():
            user = User.query.filter_by(id=current_user.id).first()
            user.firstname = form.firstname.data
            user.lastname = form.lastname.data
            user.gender = form.gender.data
            user.birthdate = form.birthdate.data
            user.role = current_user.role
            user.nhs_number = form.nhs_number.data
            user.phone = form.phone.data
            user.street = form.street.data
            user.postcode = form.postcode.data
            user.city = form.city.data
            user.email = form.email.data
            user.password = form.password.data
            user.encryption_key = current_user.encryption_key
            db.session.commit()
            flash('Account details have been updated')
            print(user)
            return redirect(url_for('users.account'))
        return render_template('account.html',
                               firstname=current_user.firstname,
                               lastname=current_user.lastname,
                               gender=current_user.gender,
                               birthdate=current_user.birthdate,
                               nhs_number=current_user.nhs_number,
                               phone=current_user.phone,
                               street=current_user.street,
                               postcode=current_user.postcode,
                               city=current_user.city,
                               email=current_user.email, update_details=update, form=form)
    return render_template('account.html',
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           gender=current_user.gender,
                           birthdate=current_user.birthdate,
                           nhs_number=current_user.nhs_number,
                           phone=current_user.phone,
                           street=current_user.street,
                           postcode=current_user.postcode,
                           city=current_user.city,
                           email=current_user.email)


# User recover password
@users_blueprint.route('/accountrecovery', methods=['POST', 'GET'])
def recover():
    """ Method that helps the user recover their
     account in case of a forgotten password"""
    email = request.form.get('email')
    step2 = request.form.get('step2')
    if request.form.get('step1'):
        # If email exists
        if User.query.filter_by(email=email).first():
            # Generate random 6 number code
            range_start = 10 ** (6 - 1)
            range_end = (10 ** 6) - 1
            security_code = randint(range_start, range_end)
            current_code = security_code
            # security code is emailed to user
            msg = Message(subject='Health Trust Account Recovery',
                          sender='healthtrust.contact@gmail.com',
                          recipients=[email])
            msg.body = 'Account recovery \n' \
                       'For: {email}\n' \
                       'Security Code: {message}'.format(email=email, message=str(current_code))
            mail.send(msg)
            flash('Account recovery code sent, please check your email')
            return render_template('password.html', step1=True, step2=False,
                                   cur_code=current_code, cur_email=email)
        # If email doesnt exist
        else:
            flash('Email provided is incorrect', 'error')
            return render_template('password.html', step1=False, step2=False, cur_email=email)

    elif step2:
        email = request.form.get('email')
        sec_code = request.form.get('valid')
        code = request.form.get('code')
        if not code:
            code = sec_code

        if code == sec_code:
            form = RecoveryForm()
            if form.validate_on_submit():
                user = User.query.filter_by(email=email).first()
                user.password = generate_password_hash(form.password.data)
                db.session.commit()
                logging.warning('SECURITY - Account Recovered [%s, %s]',
                                current_user.id, current_user.email)
                return redirect(url_for('users.login'))

            return render_template('password.html', form=form, step1=False,
                                   step2='1', cur_email=email,
                                   cur_code=sec_code, code=code)
        else:
            flash('Invalid Code', 'error')
            return render_template('password.html', step1=True,
                                   step2=False, cur_email=email, cur_code=sec_code)

    return render_template('password.html', step1=False, step2=False)


@users_blueprint.route('/faqs')
def faqs():
    """Method to return the FAQs page"""
    return render_template('faqs.html')


@users_blueprint.route('/accessibility')
def accessibility():
    """Method to return the Accessibility statement"""
    return render_template('accessibility.html')
