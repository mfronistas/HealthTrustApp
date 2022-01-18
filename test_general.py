from datetime import date, time
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
    hospital = Hospital(name='Test Hospital', street='Test Street', postcode='NE7 1AY', city='Newcastle')
    assert hospital.name == 'Test Hospital'
    assert hospital.street == 'Test Street'
    assert hospital.postcode == 'NE7 1AY'
    assert hospital.city == 'Newcastle'


def test_AppointmentModel():
    appointment = Appointment(patient_id=1, doctor_id=2, date=date(2022, 11, 24), time=time(14, 15),
                              notes='pending', site_id=1)
    assert appointment.patient_id == 1
    assert appointment.doctor_id == 2
    assert appointment.date == date(2022, 11, 24)
    assert appointment.time == time(14, 15)
    assert appointment.notes == 'pending'
    assert appointment.site_id == 1


def test_PrescriptionModel():
    prescription = Prescription(medicine_id=1, appointment_id=1, instructions='Twice a day')
    assert prescription.medicine_id == 1
    assert prescription.appointment_id == 1
    assert prescription.instructions == 'Twice a day'


def test_MedicineModel():
    medicine = Medicine(name='Moderna', type='Vaccine', dosage=5)
    assert medicine.name == 'Moderna'
    assert medicine.type == 'Vaccine'
    assert medicine.dosage == 5
