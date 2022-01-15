# IMPORTS
import logging
from datetime import datetime
from functools import wraps
from werkzeug.security import check_password_hash
import pyotp
from flask_mail import Mail, Message
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Mail
from app import db, requires_roles, mail
from models import User, generate_key
from users.forms import RegisterForm, LoginForm, ContactForm

# CONFIG

users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():

    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        nhsNr = User.query.filter_by(nhs_number=form.nhs_number.data).first()
        # if this returns a user, then the email or NHS number already exists in database

        # if email or NHS number already exists redirect user
        # back to signup page with error message so user can try again
        if user:
            flash('Email address already exists', 'error')
            return render_template('register.html', form=form)
        if nhsNr:
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
                        password=form.password.data,
                        encryption_key=generate_key()
                        )

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# Login user
@users_blueprint.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            flash('Incorrect login', 'error')
            return render_template('login.html', form=form)


        login_user(user)

        user.current_logged_in = datetime.now()
        user.last_logged_in = user.current_logged_in
        db.session.add(user)
        db.session.commit()
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin'))
        elif current_user.role == 'doctor':
            return redirect(url_for('admin.doctor'))
        else:
            return redirect(url_for('users.account'))

    return render_template('login.html', form=form)

# Contact us emailing system
@users_blueprint.route('/contactus', methods=['POST', 'GET'])
def contact_us():
    # create contact form object
    form = ContactForm()
    # if request method is POST or form is valid
    if form.validate_on_submit():
        # msg is emailed to admin
        msg = Message(subject=form.subject.data, sender='healthtrust.contact@gmail.com',
                      recipients= ['ackermandlevi@gmail.com'])
        msg.body = 'CONTACT US ENQUIRY\n' \
                   'BY: {email}\n' \
                   'Message: {message}'.format(email=form.email.data, message=form.message.data)
        mail.send(msg)
        flash('Message sent!')
        return render_template('contact.html',form=form )
    return render_template('contact.html', form=form)


# logout the current user
@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# view user account
@users_blueprint.route('/account')
@login_required
def account():
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


@users_blueprint.route('/covid')
def covid():
    return render_template('covid.html')


@users_blueprint.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@users_blueprint.route('/faqs')
def faqs():
    return render_template('faqs.html')


@users_blueprint.route('/accessibility')
def accessibility():
    return render_template('accessibility.html')

