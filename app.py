from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy

# Opening file to get database URL
f = open('databaseURL.txt', 'r')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f.readline()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
