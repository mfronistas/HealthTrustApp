from flask import Flask
from flask_sqlalchemy import SQLAlchemy, declarative_base
import sshtunnel

Base = declarative_base()
app = Flask(__name__)

tunnel = sshtunnel.SSHTunnelForwarder(
    ('linux.cs.ncl.ac.uk'), ssh_username='c0027177', ssh_password='WagonAcrossSeed12032002',
    remote_bind_address=('cs-db.ncl.ac.uk', 3306)
)
tunnel.start()

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://csc2033_team02:Stud8Box-Dew@cs-db.ncl.ac.uk/csc2033_team02:3306'

db = SQLAlchemy(app)

class User(Base):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String)

    def __init__(self, firstname):
        self.firstname = firstname

    #from dbtest2 import db\

if __name__ == '__main__':
    db.create_all()
    user = User(firstname='Jhon')
    db.session.add(user)
    db.session.commit()
    print(user)
