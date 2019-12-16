from flask import Blueprint

# Create the home Blueprint
hardware_signout = Blueprint('hardware_signout', __name__, url_prefix='/hardware')

from application.hardware_signout import controllers
