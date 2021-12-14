from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_login import LoginManager, current_user

# Opening file to get database URL
f = open('databaseURI.txt', 'r')

# Function for custom decorator for roles
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                # Redirect the user to an unauthorised notice
                return render_template('403.html')
            return f(*args, **kwargs)
        return wrapped
    return wrapper



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f.readline()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    # BLUEPRINTS
    # import blueprints
    from users.views import users_blueprint

    # register blueprints with app
    app.register_blueprint(users_blueprint)

    app.run(debug=True)
