from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cs-db.ncl.ac.uk:3306/csc2033_team02'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
db = SQLAlchemy(app)

Base = declarative_base()
class User(Base):
   __tablename__ = 'User'
   id = db.Column(Integer, primary_key=True)
   firstname = db.Column(String, unique=True)
   lastname = db.Column(String)
   password = db.Column(String)
   def __init__(self, firstname, lastname, password):
      self.firstname = firstname
      self.lastname = lastname
      self.password = password



def addpatient():
   user = User(firstname='asd', lastname='asdasd', password='123123')
   db.session.add(user)
   db.session.commit()
   print(user)

if __name__ == '__main__':
   addpatient()
   #app.run(debug=True)

