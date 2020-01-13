# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy and Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DevelopmentConfig, ProductionConfig, ReverseProxied

# Import the flask-login authentication module
from flask_login import LoginManager, login_required

# Import the flask_mail app
from flask_mail import Mail

# Admin site functionality
from flask_admin import Admin, AdminIndexView, expose, babel
from flask_admin.base import MenuLink


from flask_admin.contrib.sqla import ModelView
# Initialize pymysql for mysql support in deployment
import pymysql

pymysql.install_as_MySQLdb()

import os

# Initialize the database instance for storing all the information
db = SQLAlchemy()

# Initialize the database migrate instance
migrate = Migrate()

# Initialize the login instance
login_manager = LoginManager()


# Initialize the mail instance
# NOTE IF MAIL GIVES A RECURSION ERROR YOU MAY HAVE INSTALLED THE NEW FLASK MAIL VERSION WHICH IS CURRENTLY BUGGED
# TRY ROLLING BACK TO flask_mail version 0.9.0 instructions can be found in README
mail = Mail()

"""
New roles_required decorator for different site roles
"""
from functools import wraps
from flask import url_for, request, redirect, session


# Custom roles_required decorator
def roles_required(possible_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = int(session.get('user_id'))
            user = db_models.User.query.filter_by(id=user_id).first()
            access_granted = user.is_allowed(possible_roles)

            if(not access_granted):
                return redirect(url_for('home.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


"""
Initialize the admin site instance
"""
class HomeView(AdminIndexView):
    def __init__(self, name=None, category=None,
                 endpoint=None, url=None,
                 template='admin/index.html',
                 menu_class_name=None,
                 menu_icon_type=None,
                 menu_icon_value=None):
        super(AdminIndexView, self).__init__(name or babel.lazy_gettext('Home'),
                                             category,
                                             endpoint or 'admin',
                                             '/admin' if url is None else url,
                                             'static',
                                             menu_class_name=menu_class_name,
                                             menu_icon_type=menu_icon_type,
                                             menu_icon_value=menu_icon_value)
        self._template = template
    @login_required
    @roles_required('admin')
    @expose()
    def index(self):
        return self.render(self._template)
admin = Admin(template_mode='bootstrap3', index_view=HomeView())




"""
 Encapsulate the app in a function in order to be able to initialize it with
 various environment variables for  testing as well as versatility
"""
def create_app():
    # Define the application object

    # Change to production configuration if in production
    if os.environ["ENVIRONMENT"] == "PRODUCTION":
        # flask_app = Flask(__name__, static_url_path = '/makeuoft/static')
        flask_app = Flask(__name__)
        config_class = ProductionConfig()
        # Line for mounting the app to the /makeuoft domain
        """
        Note: ensure that ProxyPass and ReverseProxyPass are as follows on apache config:
        ProxyPass /makeuoft/static !
        ProxyPass /makeuoft http://127.0.0.1:8181/
        ProxyPassReverse /makeuoft http://ieee.utoronto.ca/makeuoft
        Alias /makeuoft/static /var/www/makeuoft/public_html/static
        """
        flask_app.wsgi_app = ReverseProxied(flask_app.wsgi_app, script_name="/makeuoft")

    else:
        flask_app = Flask(__name__)
        config_class = DevelopmentConfig()

    # Configurations taken from function argument
    flask_app.config.from_object(config_class)

    # Initialize the various models with the flask_app
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    mail.init_app(flask_app)
    admin.init_app(flask_app)
    admin.add_link(MenuLink(name='Logout', category='', url="makeuoft/auth/logout"))


    # Create a LoginManager instance
    login_manager.init_app(flask_app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = ""

    # Sample HTTP error handling
    @flask_app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    # Import a module / component using its blueprint handler variable (mod_auth)
    # from application.mod_auth.controllers import mod_auth as auth_module
    from application.home import home as home_module
    from application.auth import auth as auth_module

    from application.hardware_signout import hardware_signout as hs_module
    from application.api import api as api_module
    from application.review import review as review_module

    # Register blueprint(s) - connects each module to the main flask application
    # app.register_blueprint(xyz_module)

    flask_app.register_blueprint(home_module)
    flask_app.register_blueprint(auth_module)
    flask_app.register_blueprint(hs_module)
    flask_app.register_blueprint(api_module)
    flask_app.register_blueprint(review_module)

    # Add views for the admin site
    admin.add_view(ModelView(db_models.User, db.session))
    admin.add_view(ModelView(db_models.Role, db.session))



    return flask_app


from application import db_models

# Import the custom Command Line Interface file for custom flask commands
from application import cli
