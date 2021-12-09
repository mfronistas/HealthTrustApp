from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql

pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://csc2033_team02:Stud8Box-Dew@cs-db.ncl.ac.uk/csc2033_team02'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
db = SQLAlchemy(app)

Base = declarative_base()


class User(db.Model):
    __tablename__ = 'usertest'
    id = db.Column(Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, firstname, lastname, password):
        self.firstname = firstname
        self.lastname = lastname
        self.password = password

def init_db():
    pymysql.install_as_MySQLdb()
    db.create_all()
    user = User(firstname='Greg3', lastname='23', password='1234')
    db.session.add(user)
    db.session.commit()
    db.session.close()
    print(user)

if __name__ == '__main__':
    init_db()
    # app.run(debug=True)