from flask import (
    Blueprint,
    request,
    render_template,
    flash,
    session,
    redirect,
    url_for,
    jsonify,
)
from flask_login import login_required
from datetime import datetime

from application.auth.forms import ApplicationForm

from application.db_models import *

import json

# Import forms
from application.home.forms import MailingListForm

# Email Validation
from validate_email import validate_email

# Import the homepage Blueprint from home/__init__.py
from application.home import home


@home.route("/")
@home.route("/index", methods=["GET", "POST"])
def index():
    return render_template("home/index.html")


@home.route("mailinglist", methods=["POST"])
def mailinglist():
    # Define the json dict to return to the client
    returnDict = {}
    emailAddress = request.form.to_dict(flat=False)["email"][0]
    # Check if the email is valid
    if validate_email(emailAddress):
        # Check if email not in the system
        if MailingList.query.filter_by(email=emailAddress).first() == None:
            record = MailingList(email=emailAddress)
            db.session.add(record)
            db.session.commit()
            returnDict["success"] = True
            returnDict["message"] = "Thank you for signing up to our mailing list!"
        else:
            returnDict["success"] = False
            returnDict["error"] = "This email already exists in our records!"
    else:
        returnDict["success"] = False
        returnDict["error"] = "Please enter a valid e-mail address!"
    return jsonify(returnDict)


@home.route("/apply", methods=["GET", "POST"])
@login_required
def apply():
    form = ApplicationForm()
    return render_template("auth/application_new.html", form=form)
