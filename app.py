""" This module includes the main method of the application,
 error pages routing and home page route """
# IMPORTS
from functools import wraps
import logging
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail


# logging
class SecurityFilter(logging.Filter):
    """Class SecurityFilter for getting all logs with Security warnings"""
    def filter(self, record):
        return 'SECURITY' in record.getMessage()


fh = logging.FileHandler('healthtrust.log', 'w')
fh.setLevel(logging.WARNING)
fh.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)

logger = logging.getLogger('')
logger.propagate = False
logger.addHandler(fh)


# Function for custom decorator for roles
def requires_roles(*roles):
    """ Requires roles creates wrapper to check if the current user
     has the correct role to access a method"""
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorized access attempt [%s, %s, %s, %s]',
                                current_user.id,
                                current_user.username,
                                current_user.role,
                                request.remote_addr)
                # Redirect the user to an unauthorised notice
                return render_template('403.html')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


# Database config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthtrust.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
db = SQLAlchemy(app)
# Email Config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'healthtrust.contact@gmail.com'
app.config['MAIL_PASSWORD'] = 'Email123!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# Homepage
@app.route('/')
def index():
    """Routing the home page template"""
    return render_template('index.html')


# Error pages
@app.errorhandler(403)
def page_forbidden():
    """Routing the error 403 template"""
    return render_template('403.html'), 403


@app.errorhandler(400)
def bad_request():
    """Routing the error 400 template"""
    return render_template('400.html'), 400


@app.errorhandler(503)
def service_unavailable():
    """Routing the error 503 template"""
    return render_template('503.html'), 500


@app.errorhandler(404)
def page_not_found():
    """Routing the error 404 template"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error():
    """Routing the error 500 template"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User


    @login_manager.user_loader
    def load_user(user_id):
        """Getting the user id from login manager to determine which user is logged in"""
        return User.query.get(int(user_id))


    # BLUEPRINTS
    # import blueprints
    from users.views import users_blueprint
    from appointment.views import appointment_blueprint
    from admin.views import admin_blueprint

    # register blueprints with app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(appointment_blueprint)
    app.register_blueprint(admin_blueprint)

    app.run(debug=True)
