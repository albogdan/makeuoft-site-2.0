from flask import (
    Blueprint,
    request,
    render_template,
    flash,
    session,
    redirect,
    url_for,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user

from application.db_models import *
from application.auth.forms import (
    ApplicationForm,
    JoinTeamForm,
    LeaveTeamForm,
    RSVPForm,
)

import re
import os

# Email Validation
from validate_email import validate_email

# Import the homepage Blueprint from home/__init__.py
from application.home import home

from datetime import datetime, date


@home.route("/")
@home.route("/index", methods=["GET", "POST"])
def index():
    logged_in = not current_user.is_anonymous
    registration_starts = datetime(2019, 12, 20, 9, 0, 0)
    registration_open = datetime.now() > registration_starts
    return render_template(
        "home/index.html", logged_in=logged_in, registration_open=registration_open
    )


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
    if not current_user.is_active:
        return render_template("users/activation_required.html")

    has_submitted = (
        db.session.query(Application.id).filter_by(user_id=current_user.id).count() > 0
    )
    if has_submitted:
        return redirect(url_for("home.dashboard"))

    form = ApplicationForm()

    if form.validate_on_submit():
        resume = form.resume.data

        if not os.path.isdir(current_app.config["UPLOAD_FOLDER"]):
            os.makedirs(current_app.config["UPLOAD_FOLDER"])

        filename = "{}.pdf".format(current_user.uuid)
        resume_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        resume.save(resume_path)

        application = Application(
            user_id=current_user.id,
            preferred_name=form.preferred_name.data,
            birthday=form.birthday.data,
            gender=form.gender.data,
            ethnicity=(
                form.ethnicity_other.data
                if form.ethnicity.data == "other"
                else form.ethnicity.data
            ),
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

        return redirect(url_for("home.dashboard"))

    return render_template("users/application.html", form=form)


@home.route("/dashboard", methods=("GET", "POST"))
@login_required
def dashboard():
    def has_rsvp_expired(date_reviewed):
        """
        Checks if an RSVP has expired
        :param date_reviewed: Date the application was reviewed
        :return: (expired, expired date)
        """
        if date_reviewed < date(2020, 1, 20) and date.today() >= date(2020, 1, 31):
            # Round 1 deadline is Jan 30 23:59:59
            return True, date(2020, 1, 30).strftime("%B %-d, %Y")
        elif date.today() >= date(2020, 2, 10):
            # Final date for RSVPs
            return True, date(2020, 2, 9).strftime("%B %-d, %Y")

        return False, date(2020, 2, 9).strftime("%B %-d, %Y")

    if not current_user.is_active:
        return render_template("users/activation_required.html")

    application = (
        db.session.query(Application).filter_by(user_id=current_user.id).first()
    )
    if not application:
        return redirect(url_for("home.apply"))

    user = User.query.filter_by(id=current_user.id).first()

    if user.application[0].status:
        if (
            user.application[0].status == "accepted"
            and user.application[0].decision_sent
            and not user.application[0].rsvp_accepted
        ):

            expired, expired_date = has_rsvp_expired(user.application[0].date_reviewed)
            if expired:
                return render_template("users/rsvp_missed.html", rsvp_deadline=expired_date)

            rsvp_form = RSVPForm()

            if rsvp_form.validate_on_submit():
                user.application[0].rsvp_accepted = True
                db.session.commit()

                return render_template("users/accepted.html", user=user)

            return render_template(
                "users/rsvp.html", user=current_user, rsvp_form=rsvp_form
            )

        elif user.application[0].status == "accepted" and user.application[0].rsvp_accepted:
            return render_template("users/accepted.html", user=user)

        elif user.application[0].status == "rejected" and user.application[0].decision_sent:
            return render_template("users/rejected.html")

        elif user.application[0].status == "waitlisted" and user.application[0].decision_sent:
            # Waitlisted users are still allowed to make and join a team
            if not current_user.team:
                join_team_form = JoinTeamForm()
                if join_team_form.validate_on_submit():
                    team = Team.query.filter_by(team_code=join_team_form.team_code.data).first()

                    if not team:
                        join_team_form.team_code.errors.append(
                            f"Team {join_team_form.team_code.data} does not exist"
                        )
                    elif len(team.team_members) >= Team.max_members:
                        join_team_form.team_code.errors.append(f"Team {team.team_code} is full")
                    else:
                        user.team = team
                        db.session.commit()

                        return redirect(url_for("home.dashboard"))

                return render_template(
                    "users/waitlisted.html",
                    user=current_user,
                    join_team_form=join_team_form,
                )
            else:
                # If the user is on a team, setup the form to leave one
                leave_team_form = LeaveTeamForm()
                if leave_team_form.validate_on_submit():
                    user.team = None
                    db.session.commit()

                    return redirect(url_for("home.dashboard"))

                return render_template(
                    "users/waitlisted.html",
                    user=current_user,
                    leave_team_form=leave_team_form,
                )

    if not current_user.team:
        # If the user is not on a team, setup the form to join one
        join_team_form = JoinTeamForm()
        if join_team_form.validate_on_submit():
            team = Team.query.filter_by(team_code=join_team_form.team_code.data).first()

            if not team:
                join_team_form.team_code.errors.append(
                    f"Team {join_team_form.team_code.data} does not exist"
                )
            elif len(team.team_members) >= Team.max_members:
                join_team_form.team_code.errors.append(f"Team {team.team_code} is full")
            else:
                user.team = team
                db.session.commit()

                return redirect(url_for("home.dashboard"))

        return render_template(
            "users/post_application.html",
            user=current_user,
            join_team_form=join_team_form,
        )

    else:
        # If the user is on a team, setup the form to leave one
        leave_team_form = LeaveTeamForm()
        if leave_team_form.validate_on_submit():
            user.team = None
            db.session.commit()

            return redirect(url_for("home.dashboard"))

        return render_template(
            "users/post_application.html",
            user=current_user,
            leave_team_form=leave_team_form,
        )
