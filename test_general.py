from datetime import date
from models import Prescription, User, Hospital, Appointment, Medicine



def test_UserModel():
    user = User(firstname='John', lastname='Doe', gender='Male', birthdate=date(2002, 11, 24), role='patient',
                nhs_number='0101010101', phone=7908579733, street='Baker Street', postcode='NE7 7AY',
                city='Newcastle', email='DJohn@email.com', password='Password')
    assert user.firstname == 'John'
    assert user.lastname == 'Doe'
    assert user.gender == 'Male'
    assert user.birthdate == date(2002, 11, 24)
    assert user.role == 'patient'
    assert user.nhs_number == '0101010101'
    assert user.phone == 7908579733
    assert user.street == 'Baker Street'
    assert user.postcode == 'NE7 7AY'
    assert user.city == 'Newcastle'
    assert user.email == 'DJohn@email.com'
    assert user.password != 'Password'

def test_HospitalModel():

    pass

def test_AppointmentModel():
    pass

def test_PrescriptionModel():
    pass

def test_MedicineModel():
    pass