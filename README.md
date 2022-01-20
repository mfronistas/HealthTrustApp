# Health Trust App
Software engineering project 2033 - Team 2

### How to run the application succesfully

Before running the application please ensure all the requirements (found in the requirements.txt file) are installed.

The application should be run through python rather than flask as this ensures the proper operation of all the app's functions.

### User Information

The application has 3 levels of user. These are Patient, Doctor and Admin.

You can find login details for a pre-made patient, doctor and admin account at the bottom of this file.

Patient accounts can be created easily using the register form. When creating a patient account it is **important** to use a **real email address** as the user will be emailed their encryption key which they can use in Authy to generate their one-time pinkey for each time they log in.

A patient can book appointments at a selected hospital and at a specified time in the book appointment form. They can then view and cancel these in the view appointments page.

A doctor can view their upcoming appointments and are able to cancel them, this will automatically email the patient to inform them of this. A doctor can also make notes about each appointment, furthermore they can prescribe patients with medication if/when necessary.

The admin user is used to manage permissions across the site and view security logs. They can create doctor accounts, add medications and add new hospitals using the pages they can access.

To see some features of the programme we recommend creating your own patient and doctor user using the built-in features in the software as some features of the site require accounts with real email addresses (e.g. Password Reset, Adding Doctors, Adding Users and Contact Us.)

### PATIENT ACCOUNT LOGIN DETAILS:
**email**: jsmith@email.com
**password**: Password123
**encryption key**: 3GUKRPZJDYM63M4WAEOXJHDW5QBCNRDS

### DOCTOR ACCOUNT LOGIN DETAILS:
**email**: manderson@hospital.com
**password**: VerySecure890
**encryption key**: UAPTEYF3HKORWDYMSYHAVCBBSAML6WAX

### ADMIN ACCOUNT LOGIN DETAILS:
**email**: admin@email.com
**password**: IaTaSoMrU99
**encryption key**: P5DXTWRQUR6ZLG6WFQSPC7P3D7XDUFDS
