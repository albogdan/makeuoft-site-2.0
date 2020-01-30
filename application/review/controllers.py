import math
import os

from flask import render_template, request, send_file, current_app
from flask_login import login_required

from application import roles_required
from application.review import review, manager
from application.review.forms import MailerForm

# Number of teams to display on one page
page_size = 10


@review.route("/")
@login_required
@roles_required(["staff"])
def index():
    page = int(request.args.get("page", 1))
    status = request.args.get("status", "all").lower()
    search = request.args.get("search", "").lower().strip() or None

    statuses = [
        ("All", "all", status == "all"),
        ("Waiting", "waiting", status == "waiting"),
        ("Waitlisted", "waitlisted", status == "waitlisted"),
        ("Accepted", "accepted", status == "accepted"),
        ("Rejected", "rejected", status == "rejected"),
    ]

    teams_and_users_query = manager.get_teams_and_users(status=status, search=search)

    num_pages = math.ceil(teams_and_users_query.count() / page_size)
    page = min(page, num_pages)
    offset = (page - 1) * page_size

    teams_and_users = teams_and_users_query.limit(page_size).offset(offset).all()
    num_with_status = manager.get_num_applications_with_status(status)

    api_url = (
        "/api"
        if "ENV" in current_app.config and current_app.config["ENV"] == "development"
        else "/makeuoft/api"
    )

    return render_template(
        "review/portal.html",
        teams_and_users=teams_and_users,
        page=page,
        num_pages=num_pages,
        api_url=api_url,
        statuses=statuses,
        num_applications_with_status=num_with_status,
        search=search
    )


@review.route("/resumes/<uuid>/")
@login_required
@roles_required(["staff"])
def resumes(uuid):
    user = manager.get_user(uuid)
    resume_filename = user.application[0].resume_path.split("/")[-1]
    resume_path = os.path.abspath(
        os.path.join(current_app.config["UPLOAD_FOLDER"], resume_filename)
    )
    if not os.path.isfile(resume_path):
        return "Resume not found", 404

    return send_file(resume_path)


@review.route("/mailer/", methods=["GET", "POST"])
@login_required
@roles_required(["admin"])
def mailer():
    """
    View to manage sending of emails to applicants by status
    """
    num_sent = None

    form = MailerForm()

    if form.validate_on_submit():
        num_sent = manager.send_emails_by_status(form.mailer.data, form.date_start.data, form.date_end.data)

    return render_template("review/mailer.html", form=form, num_sent=num_sent)
