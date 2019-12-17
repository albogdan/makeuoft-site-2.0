from flask import Blueprint

# Create the admin Blueprint
api = Blueprint('api', __name__, url_prefix='/api')


from application.api import controllers
