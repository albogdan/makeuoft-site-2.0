from flask import render_template

from flask_login import login_required

# Import the homepage Blueprint from home/__init__.py
from application.hardware_signout import hardware_signout

from application import roles_required


@hardware_signout.route("/")
@hardware_signout.route("/index", methods=["GET", "POST"])
@login_required
@roles_required(["admin"])
def index():
    return render_template("hardware_signout/index.html")
