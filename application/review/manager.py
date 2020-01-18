from datetime import date

import sqlalchemy as sa
from sqlalchemy.sql.expression import func

from application import db
import application.db_models as models

from application import mail
from flask_mail import Message

from flask import render_template

reviewer_fields = {"status", "evaluator_comments", "experience", "interest", "quality"}


def filter_by_application_status(q, status):
    if status == "all":
        return q
    elif status == "waiting":
        return q.filter(models.Application.status.is_(None))

    return q.filter(models.Application.status == status)


def get_teams(status="all"):
    """
    Return a query of teams, ordered by the last application
    submission time of a member of the team
    """

    q = models.Team.query.join(models.User).join(
        models.Application, models.Application.user_id == models.User.id
    )
    q = filter_by_application_status(q, status)
    q = q.group_by(models.User.team_id).order_by(
        func.max(models.Application.submitted_time).asc()
    )

    return q


def get_teamless_users(status="all"):
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
    q = q.order_by(models.Application.submitted_time.asc())

    return q


def get_ordering_of_teams_and_users(status="all"):
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

    teams_query = get_teams(status=status).with_entities(
        sa.null().label("user_id"),
        models.Team.id.label("team_id"),
        func.max(models.Application.submitted_time).label("submitted_time"),
    )

    users_query = get_teamless_users(status=status).with_entities(
        models.User.id.label("user_id"),
        sa.null().label("team_id"),
        models.Application.submitted_time.label("submitted_time"),
    )

    combined = teams_query.union(users_query).order_by(
        models.Application.submitted_time
    )

    return combined


def get_teams_and_users(limit=None, offset=None, status="all"):
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
    orderings = get_ordering_of_teams_and_users(status=status).subquery()

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


def set_user_application_attribute(uuid, attr, val, evaluator_id=None):
    user = get_user(uuid)
    setattr(user.application[0], attr, val)
    user.application[0].date_reviewed = date.today()
    user.application[0].evaluator_id = evaluator_id
    db.session.commit()


def get_team(team_code):
    return models.Team.query.filter(models.Team.team_code == team_code).first()


def set_team_application_attribute(team_code, attr, val, evaluator_id=None):
    team = get_team(team_code)
    for user in team.team_members:
        setattr(user.application[0], attr, val)
        user.application[0].date_reviewed = date.today()
        user.application[0].evaluator_id = evaluator_id
    db.session.commit()


def send_emails_by_status(status):
    status_to_template = {
        "accepted": ("You've been accepted to MakeUofT 2020!", "mails/accepted.html"),
        "rejected": (
            "We couldn't accept you into MakeUofT 2020",
            "mails/rejected.html",
        ),
        "waitlisted": (
            "You're on the waitlist to MakeUofT 2020",
            "mails/waitlisted.html",
        ),
    }

    users = models.User.query.join(
        models.Application, models.Application.user_id == models.User.id
    ).filter(models.Application.status == status)

    for user in users:
        # Send the verification email
        msg = Message(status_to_template[status][0], recipients=[user.email])
        msg.html = render_template(
            status_to_template[status][1],
            preferred_name=user.application[0].preferred_name,
        )
        mail.send(msg)
