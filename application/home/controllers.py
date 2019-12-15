from flask import (
    Blueprint,
    request,
    render_template,
    flash,
    session,
    redirect,
    url_for,
    jsonify,
    current_app
)
from flask_login import login_required, current_user
from datetime import datetime

from application.db_models import *
from application.auth.forms import ApplicationForm

from hashlib import md5
import re
import os
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


@home.route("/apply", methods=("GET", "POST"))
@login_required
def apply():
    form = ApplicationForm()

    if form.validate_on_submit():
        resume = form.resume.data

        if not os.path.isdir(current_app.config["UPLOAD_FOLDER"]):
            os.makedirs(current_app.config["UPLOAD_FOLDER"])

        filename = "{}.pdf".format(md5(current_user.email.encode()).hexdigest())
        resume_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        resume.save(resume_path)

        application = Application(
            user_id=current_user.id,
            preferred_name=form.preferred_name.data,
            birthday=form.birthday.data,
            gender=form.gender.data,
            ethnicity=(form.ethnicity_other.data if form.ethnicity.data == "other" else form.ethnicity.data),
            tshirt_size=form.tshirt_size.data,
            dietary_restrictions=form.dietary_restrictions.data,
            phone_number=re.sub(r"[^0-9]", "", form.phone_number.data),
            school=form.school.data,
            study_level=form.study_level.data,
            program=form.program.data,
            graduation_year=form.grad_year.data,
            resume_path=resume_path,
            q1_prev_hackathon=form.q1_prev_hackathon.data,
            q2_why_participate=form.q2_why_participate.data,
            q3_hardware_exp=form.q3_hardware_exp.data,
            referral_source=form.how_you_hear.data,
            mlh_conduct_agree=form.mlh_conduct.data,
            mlh_data_agree=form.mlh_data.data,
            resume_sharing=form.resume_share.data,
            age_confirmation=form.age_confirmation.data,
        )
        db.session.add(application)
        db.session.commit()

    return render_template("apply/application.html", form=form)
