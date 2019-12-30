import os
from dotenv import load_dotenv

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load the environment file
load_dotenv(os.path.join(BASE_DIR, ".flaskenv"))


# DevelopmentConfig
class DevelopmentConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root@127.0.0.1:3306/makeuoft"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_CONNECT_OPTIONS = {}
    THREADS_PER_PAGE = 2
    CSRF_ENABLED = True
    SECRET_KEY = "secret"
    MAIL_SERVER = "smtp.gmail.com"  # assuming gmail is being used
    MAIL_USERNAME = "makeuoft@gmail.com"  # change this
    MAIL_PASSWORD = ""
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = "makeuoft@gmail.com"
    MAIL_USE_TLS = False
    UPLOAD_FOLDER = "resumes/"
    ALLOWED_EXTENSIONS = {"pdf"}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    FLASK_ADMIN_SWATCH = "cerulean"


# ProductionConfig class to encapsulate the config varaibles
class ProductionConfig(object):
    # Config variables
    # Statement for enabling the development environment
    # DEBUG = True

    # Define the database - we are working with
    # SQLite for this example
    # For mysql: app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
    if os.environ["ENVIRONMENT"] == "PRODUCTION":
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:3306/{}?unix_socket=/run/mysqld/mysqld.sock".format(
            os.environ["DB_USER_NAME"],
            os.environ["DB_USER_PW"],
            os.environ["DB_SERVER"],
            os.environ["DB_NAME"],
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_CONNECT_OPTIONS = {}

    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for
    # signing the data.
    # CSRF_SESSION_KEY = os.environ.get('CSRF_SECRET_KEY') or "secret"

    # Secret key for signing cookies
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # File upload settings
    UPLOAD_FOLDER = "/var/resumes/"
    ALLOWED_EXTENSIONS = {"pdf"}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    FLASK_ADMIN_SWATCH = "cerulean"

    # Mail settings
    MAIL_SERVER = "smtp.gmail.com"  # assuming gmail is being used
    MAIL_USERNAME = os.environ.get("EMAIL_SENDER_USR")  # change this
    MAIL_PASSWORD = os.environ.get("EMAIL_SENDER_PSW")
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = ("MakeUofT Team", os.environ.get("EMAIL_SENDER_USR"))
    MAIL_USE_TLS = False


# ReverseProxied Configurations for app mounting to subdomain (i.e., /makeuoft)
class ReverseProxied(object):
    def __init__(self, app, script_name=None, scheme=None, server=None):
        self.app = app
        self.script_name = script_name
        self.scheme = scheme
        self.server = server

    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "") or self.script_name
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]
        scheme = environ.get("HTTP_X_SCHEME", "") or self.scheme
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        server = environ.get("HTTP_X_FORWARDED_SERVER", "") or self.server
        if server:
            environ["HTTP_HOST"] = server
        return self.app(environ, start_response)
