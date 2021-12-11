import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
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
    if len(phonenumber) < 13 or number_amount != 11:
        raise ValidationError(f"Phone number is incorrect")
    if phonenumber[4] != '-' or phonenumber[8] != '-':
        raise ValidationError(f"Phone number must be entered in a XXXX-XXX-XXXX format.")


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
    birthday = StringField(validators=[InputRequired(), DataRequired()])
    nhs_number = StringField(validators=[InputRequired, Length(min=12,max=12,
                                                               message="NHS number must contain 12 numbers")])
    phone = StringField(validators=[InputRequired(), phone_validation])
    street = StringField(validators=[InputRequired(), char_validation()])
    postcode = StringField(validators=[InputRequired()])
    city = StringField(validators=[InputRequired(), char_validation()])
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
