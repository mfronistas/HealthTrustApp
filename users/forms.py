"""This module contains all the forms used in this application and
validation to make sure that data submitted in the form are correct"""
import re
from datetime import date
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, \
    SelectField, TextAreaField
from wtforms.validators import Email, ValidationError, Length, EqualTo, InputRequired, DataRequired


# check if there are any characters that are not allowed in a string
def char_validation(form, field):
    """Method to check if any illegal characters are contained in a string"""
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed.")


# check if the phone number has enough numbers and correct the format
def phone_validation(form, field):
    """Method to check the correct length of a phone number"""
    phonenumber = field.data
    number_amount = number_checker(phonenumber)
    if number_amount < 11:
        raise  ValidationError("Phone number is too short")
    if number_amount > 11:
        raise ValidationError("Phone number is too long")


# check the amount of numbers in a string
def number_checker(number):
    """Method to check if the numbers in the string are an actual numbers"""
    possible_numbers = "0123456789"
    current_amount = 0
    for char in number:
        if char in possible_numbers:
            current_amount += 1
    return current_amount


# REGISTER FORM
class RegisterForm(FlaskForm):
    """Class for creating a register form and validating its fields"""
    firstname = StringField(validators=[InputRequired(), char_validation])
    lastname = StringField(validators=[InputRequired(), char_validation])
    gender = SelectField(
        'Gender Type',
        choices=[('Male', 'Male'), ('Female', 'Female'),
                 ('Other', 'Other')], validators=[InputRequired()])
    birthdate = DateField(validators=[InputRequired(), DataRequired()])
    nhs_number = StringField(validators=[InputRequired(),
                                         Length(min=10, max=10,
                                                message="NHS number must contain 10 numbers")])
    phone = StringField(validators=[InputRequired(), phone_validation])
    street = StringField(validators=[InputRequired()])
    postcode = StringField(validators=[InputRequired()])
    city = StringField(validators=[InputRequired()])
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired(),
                                         Length(min=6, max=12,
                                                message="Password must be between "
                                                        "6 and 12 characters long.")])
    confirm_password = PasswordField(validators=[InputRequired(),
                                                 EqualTo('password',
                                                         message="Passwords must be the same.")])
    submit = SubmitField()

    # check if the password has met all the requirements
    def validate_password(self, password):
        """Method to validate a password to follow specific restrictions
         for the purpose of it being secure enough"""
        password_check = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*\W)')
        if not password_check.match(self.password.data):
            raise ValidationError(message="Password must contain at least 1 small letter,"
                                          " 1 capital letter, 1 digit and 1 special character.")


# LOGIN FORM
class LoginForm(FlaskForm):
    """Class for creating a login form and validating its fields"""
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired()])
    pin = StringField(validators=[InputRequired(), Length(min=6, max=6,
                                                          message='Pin must be 6 digits long')])
    submit = SubmitField()


# APPOINTMENT FORM
class AppointmentForm(FlaskForm):
    """Class for creating an appointment form and validating its fields"""
    date = DateField(validators=[InputRequired()])
    patient_id = StringField()
    submit = SubmitField()

    # Check that appointment isnt in the past
    def validate_date(form, field):
        """Method to validate that the date that the user is trying
         to choose to book an appointment is not in the past"""
        if form.date.data <= date.today():
            flash('Please choose a valid date')
            raise ValidationError("Please choose a valid date")


# DOCTOR FORM
class DoctorForm(FlaskForm):
    """Class for creating a doctor form and validating its fields"""
    firstname = StringField(validators=[InputRequired(), char_validation])
    lastname = StringField(validators=[InputRequired(), char_validation])
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired(),
                                         Length(min=6, max=12,
                                                message="Password must be "
                                                        "between 6 and 12 characters long.")])
    gender = SelectField(
        'Gender Type',
        choices=[('Male', 'Male'), ('Female', 'Female'),
                 ('Other', 'Other')], validators=[InputRequired()])
    birthdate = DateField(validators=[InputRequired(), DataRequired()])
    phone = StringField(validators=[InputRequired(), phone_validation])
    street = StringField(validators=[InputRequired()])
    postcode = StringField(validators=[InputRequired()])
    city = StringField(validators=[InputRequired()])
    submit = SubmitField()

    def validate_password(self, password):
        """Method to validate a password to follow specific restrictions
                 for the purpose of it being secure enough"""
        password_check = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*\W)')
        if not password_check.match(self.password.data):
            raise ValidationError(message="Password must contain at least 1 small letter,"
                                          " 1 capital letter, 1 digit and 1 special character.")


# MEDICINE FORM
class MedicineForm(FlaskForm):
    """Class for creating a medicine form and validating its fields"""
    name = StringField(validators=[InputRequired()])
    type = StringField(validators=[InputRequired()])
    dosage = StringField(validators=[InputRequired()])
    submit = SubmitField()


# UPDATE NOTES FORM
class UpdateNotesForm(FlaskForm):
    """Class for creating an update notes form and validating its fields"""
    notes = TextAreaField(validators=[InputRequired()])


# PRESCRIPTION FORM
class PrescriptionForm(FlaskForm):
    """Class for creating a prescription form and validating its fields"""
    instructions = TextAreaField(validators=[InputRequired()])
    submit = SubmitField()


# HOSPITAL FORM
class HospitalForm(FlaskForm):
    """Class for creating a hospital form and validating its fields"""
    name = StringField(validators=[InputRequired()])
    street = StringField(validators=[InputRequired()])
    postcode = StringField(validators=[InputRequired()])
    city = StringField(validators=[InputRequired()])
    submit = SubmitField()


# CONTACT FORM
class ContactForm(FlaskForm):
    """Class for creating a contact form and validating its fields"""
    email = StringField(validators=[InputRequired(), Email()])
    subject = StringField(validators=[InputRequired()])
    message = TextAreaField(validators=[InputRequired()])
    submit = SubmitField()


# RECOVERY FORM
class RecoveryForm(FlaskForm):
    """Class for creating a recovery form and validating its fields"""
    password = PasswordField(validators=[InputRequired(),
                                         Length(min=6, max=12,
                                                message="Password must be "
                                                        "between 6 and 12 characters long.")])
    confirm_password = PasswordField(validators=[InputRequired(),
                                                 EqualTo('password',
                                                         message="Passwords must be the same.")])
    submit = SubmitField()

    def validate_password(self, password):
        """Method to validate a password to follow specific restrictions
                 for the purpose of it being secure enough"""
        password_check = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*\W)')
        if not password_check.match(self.password.data):
            raise ValidationError(message="Password must contain at least 1 small letter,"
                                          " 1 capital letter, 1 digit and 1 special character.")
