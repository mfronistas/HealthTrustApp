from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_login import LoginManager, current_user



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

# Opening file to get database URL
f = open('databaseURL.txt', 'r')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f.readline()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
db = SQLAlchemy(app)

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Error pages
@app.errorhandler(403)
def page_forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400

@app.errorhandler(503)
def service_unavailable(error):
    return render_template('503.html'), 500

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


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
