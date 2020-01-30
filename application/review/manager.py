from datetime import date

import sqlalchemy as sa
from sqlalchemy.sql.expression import func
from sqlalchemy import or_

from application import db
import application.db_models as models

from application import mail
from flask_mail import Message

from flask import render_template, current_app

reviewer_fields = {"status", "evaluator_comments", "experience", "interest", "quality"}


def get_num_applications_with_status(status):
    if status == "all":
        q = models.Application.query
    elif status == "waiting":
        q = models.Application.query.filter(models.Application.status.is_(None))
    elif status == "attending":
        q = models.Application.query.filter(
            models.Application.status == "accepted",
            models.Application.rsvp_accepted.is_(True),
        )
    else:
        q = models.Application.query.filter(models.Application.status == status)

    return q.count()


def filter_by_application_status(q, status):
    if status == "all":
        return q
    elif status == "waiting":
        return q.filter(models.Application.status.is_(None))
    elif status == "attending":
        return q.filter(
            models.Application.status == "accepted",
            models.Application.rsvp_accepted.is_(True),
        )

    return q.filter(models.Application.status == status)


def _search(q, search=None):
    if not search:
        return q


def get_teams(status="all", search=None):
    """
    Return a query of teams, ordered by the last application
    submission time of a member of the team
    """

    q = models.Team.query.join(models.User).join(
        models.Application, models.Application.user_id == models.User.id
    )
    q = filter_by_application_status(q, status)

    if search:
        q = q.filter(
            or_(
                models.User.first_name.like(f"%{search}%"),
                models.User.last_name.like(f"%{search}%"),
                models.User.uuid.like(f"%{search}%"),
                models.User.email.like(f"%{search}%"),
                models.Team.team_code == search,
            )
        )

    q = q.group_by(models.User.team_id).order_by(
        func.max(models.Application.submitted_time).asc()
    )

    return q


def get_teamless_users(status="all", search=None):
    """
    The review site deals with two groupings: Users on a team, and
    users not on a team. These get interleaved together in order
    of submission time see `get_teams` for a definition of that for
    a team.

    Return a query of users who aren't on a team, who have submitted
    an application, ordered by submission
    time.
    """

    q = models.User.query.join(
        models.Application, models.Application.user_id == models.User.id
    ).filter(models.User.team_id.is_(None))
    q = filter_by_application_status(q, status)

    if search:
        q = q.filter(
            or_(
                models.User.first_name.like(f"%{search}%"),
                models.User.last_name.like(f"%{search}%"),
                models.User.uuid.like(f"%{search}%"),
                models.User.email.like(f"%{search}%"),
            )
        )

    q = q.order_by(models.Application.submitted_time.asc())

    return q


def get_ordering_of_teams_and_users(status="all", search=None):
    """
    The order teams or teamless users appear in the review portal
    is by their respective submission dates. This function
    return a query with the following structure:

    user_id | team_id | submitted_time
    --------+---------+--------------------
    34      | <null>  | 2019-12-20 12:03:05
    35      | <null>  | 2019-12-20 12:12:38
    <null>  | 43      | 2019-12-20 13:22:03
    ...     | ...     | ...
    """

    teams_query = get_teams(status=status, search=search).with_entities(
        sa.null().label("user_id"),
        models.Team.id.label("team_id"),
        func.max(models.Application.submitted_time).label("submitted_time"),
    )

    users_query = get_teamless_users(status=status, search=search).with_entities(
        models.User.id.label("user_id"),
        sa.null().label("team_id"),
        models.Application.submitted_time.label("submitted_time"),
    )

    combined = teams_query.union(users_query).order_by(
        models.Application.submitted_time
    )

    return combined


def get_teams_and_users(limit=None, offset=None, status="all", search=None):
    """
    Returns a list of tuples (actually sqlalchemy result collections) of
        (
            submitted_time,
            models.User,
            models.Team,
        )
    ordered by submitted_time with the appropriate limit and offset.

    Only one of models.User and models.Team will be not None
    for a given tuple, indicating teamless users.

    Tuple elements can be accessed by .submitted_time, .User, and .Team
    """
    orderings = get_ordering_of_teams_and_users(status=status, search=search).subquery()

    results = (
        db.session.query(orderings.c.submitted_time, models.User, models.Team)
        .outerjoin(models.User, orderings.c.user_id == models.User.id)
        .outerjoin(models.Team, orderings.c.team_id == models.Team.id)
        .order_by(orderings.c.submitted_time.asc())
    )

    if limit:
        results = results.limit(limit)

        if offset:
            results = results.offset(offset)

    return results


def get_user(uuid):
    return models.User.query.filter(models.User.uuid == uuid).first()


def _modify_user(user, attr, val, evaluator_id=None):
    if (
        attr == "status"
        and user.application[0].status in {"accepted", "rejected"}
        and user.application[0].decision_sent
    ):
        # Status can't be changed for accepted or rejected users after notifying them
        return

    if attr == "status" and user.application[0].status != val:
        # When the user is waitlisted, allow their application status to be changed,
        # and allow emails to be sent to them again
        user.application[0].decision_sent = False

    setattr(user.application[0], attr, val)
    user.application[0].date_reviewed = date.today()
    user.application[0].evaluator_id = evaluator_id
    db.session.commit()


def set_user_application_attribute(uuid, attr, val, evaluator_id=None):
    user = get_user(uuid)
    _modify_user(user, attr, val, evaluator_id)


def get_team(team_code):
    return models.Team.query.filter(models.Team.team_code == team_code).first()


def set_team_application_attribute(team_code, attr, val, evaluator_id=None):
    team = get_team(team_code)
    for user in team.team_members:
        _modify_user(user, attr, val, evaluator_id)


def send_emails_by_status(status, date_start, date_end):
    """
    Send emails informing applicants of the decision on their application

    Sending emails will set the `decision_sent` flag to True on the user's application,
    after which no further decision emails can be sent to them. This flag also prevents
    the user's status from being changed if it was accepted or rejected, but it can be
    changed if they were waitlisted. Doing so will set the `decision_sent` flag back to
    False, allowing them to be notified again. (This happens above in _modify_user)

    """
    status_to_template = {
        "accepted": (
            "Congratulations, you’ve been accepted to MakeUofT 2020! ",
            "mails/accepted.html",
        ),
        "rejected": ("MakeUofT 2020 Application Decision", "mails/rejected.html"),
        "waitlisted": ("MakeUofT 2020 Application Decision", "mails/waitlisted.html"),
    }

    users = (
        models.User.query.join(
            models.Application, models.Application.user_id == models.User.id
        )
        .filter(models.Application.status == status)
        .filter(models.Application.date_reviewed >= date_start)
        .filter(models.Application.date_reviewed <= date_end)
        .filter(models.Application.decision_sent.is_(False))
    ).all()

    num_sent = 0

    with mail.connect() as conn:
        for user in users:
            msg = Message(status_to_template[status][0], recipients=[user.email])
            msg.html = render_template(status_to_template[status][1], user=user)
            if current_app.config["DEBUG"]:
                print(msg)
            else:
                conn.send(msg)
            user.application[0].decision_sent = True
            db.session.commit()

            num_sent += 1

    return num_sent
