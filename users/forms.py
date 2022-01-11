import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField
from wtforms.validators import Email, ValidationError, Length, EqualTo, InputRequired, DataRequired


# check if there are any characters that are not allowed in a string
def char_validation(form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(f"Character {char} is not allowed.")


# check if the phone number has enough numbers and correct the format
def phone_validation(form, field):
    phonenumber = field.data
    number_amount = number_checker(phonenumber)
    if number_amount != 11:
        raise ValidationError(f"Phone number is incorrect")


# check the amount of numbers in a string
def number_checker(number):
    possible_numbers = "0123456789"
    current_amount = 0
    for char in number:
        if char in possible_numbers:
            current_amount += 1
    return current_amount


# REGISTER FORM    TODO: check if fields have all the specific restrictions they require
class RegisterForm(FlaskForm):
    firstname = StringField(validators=[InputRequired(), char_validation])
    lastname = StringField(validators=[InputRequired(), char_validation])
    gender = StringField(validators=[InputRequired()])
    birthdate = DateField(validators=[InputRequired(), DataRequired()])
    nhs_number = StringField(validators=[InputRequired(), Length(min=10, max=10,
                                                                 message="NHS number must contain 10 numbers")])
    phone = StringField(validators=[InputRequired(), phone_validation])
    street = StringField(validators=[InputRequired()])
    postcode = StringField(validators=[InputRequired()])
    city = StringField(validators=[InputRequired()])
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired(),
                                         Length(min=6, max=12,
                                                message="Password must be between 6 and 12 characters long.")])
    confirm_password = PasswordField(validators=[InputRequired(),
                                                 EqualTo('password', message="Passwords must be the same.")])
    submit = SubmitField()

    # check if the password has met all the requirements
    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*\W)')
        if not p.match(self.password.data):
            raise ValidationError(message="Password must contain at least 1 small letter,"
                                          " 1 capital letter, 1 digit and 1 special character.")


# LOGIN FORM
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired()])
    submit = SubmitField()


# APPOINTMENT FORM
class AppointmentForm(FlaskForm):
    # TODO Might be drop down box instead, patient will also be completed automatically -> see appointments.views
    patient = StringField(validators=[InputRequired()])
    doctor = StringField(validators=[InputRequired()])
    date = StringField(validators=[InputRequired()])
    time = StringField(validators=[InputRequired()])
    notes = StringField(validators=[InputRequired()])
    site = StringField(validators=[InputRequired()])

