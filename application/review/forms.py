from flask_wtf import FlaskForm

from wtforms import (
    SelectField,
    SubmitField,
)
from wtforms.fields.html5 import DateField

from wtforms.validators import DataRequired


class MailerForm(FlaskForm):
    """
    Form to launch mailers for applicants to inform them of the status
    of their applications.
    """

    date_start = DateField(
        "Start Date",
        validators=[DataRequired(message="Required"),],
        render_kw={"placeholder": "YYYY-MM-DD"},
    )

    date_end = DateField(
        "End Date",
        validators=[DataRequired(message="Required"),],
        render_kw={"placeholder": "YYYY-MM-DD"},
    )

    mailer = SelectField(
        "Applicant statuses to send to",
        choices=[
            ("", ""),
            ("accepted", "Accepted"),
            ("waitlisted", "Waitlisted"),
            ("rejected", "Rejected"),
        ],
        validators=[DataRequired(),],
    )

    submit = SubmitField("Submit", render_kw={"class": "button"})
