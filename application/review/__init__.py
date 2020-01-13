from flask import Blueprint

# Create the home Blueprint
review = Blueprint('review', __name__, url_prefix='/review')

from application.review import controllers
