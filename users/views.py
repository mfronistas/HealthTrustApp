# IMPORTS
import logging
from datetime import datetime
from functools import wraps
from werkzeug.security import check_password_hash
import pyotp

from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required

from app import db, requires_roles
from models import User
from users.forms import RegisterForm, LoginForm

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
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('register.html', form=form)

        # create a new user with the form data
        new_user = User(firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        gender=form.gender.data,
                        birthdate=form.birthdate.data,
                        role=form.role.data,
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
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            flash('Incorrect login')
        return render_template('login.html', form=form)

        login_user(user)

        user.current_logged_in = datetime.now()
        user.last_logged_in = user.current_logged_in
        db.session.add(user)
        db.session.commit()




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
                           firstname=current_user.firstname.data,
                           lastname=current_user.lastname.data,
                           gender=current_user.gender.data,
                           birthdate=current_user.birthdate.data,
                           nhs_number=current_user.nhs_number.data,
                           phone=current_user.phone.data,
                           street=current_user.street.data,
                           postcode=current_user.postcode.data,
                           city=current_user.city.data,
                           email=current_user.email.data)