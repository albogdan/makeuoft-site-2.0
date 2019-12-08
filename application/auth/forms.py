from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    FileField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.fields.html5 import DateField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    NumberRange,
    Regexp,
    ValidationError,
)
from application.db_models import Users
from application.auth.validators import DataRequiredIfOtherFieldEmpty


class LoginForm(FlaskForm):
    email = StringField("E-Mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """
    Registration that allows customers to register with their first name,
    last name, email and a password
    """

    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Register")

    def validate_email(self, email):
        search_email = Users.query.filter_by(email=email.data).first()
        if search_email is not None:
            raise ValidationError("Please use a different email address.")


class ApplicationForm(FlaskForm):
    """
    Application form that takes all of the information of contestants
    and puts it into the database
    """

    # First and last name are redundant with an associated user - preferred name could be useful
    preferred_name = StringField("Preferred Name", validators=[DataRequired()])
    birthday = DateField("Birthday", validators=[DataRequired()])
    gender = SelectField(
        "Gender",
        choices=[
            ("", ""),
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
            ("no-answer", "Prefer not to answer"),
        ],
        validators=[DataRequired()],
    )
    ethnicity = SelectField(
        "Ethnicity",
        choices=[
            ("", ""),
            ("american-native", "American Indian or Alaskan Native"),
            ("asian-pacific-islander", "Asian / Pacific Islander"),
            ("black-african-american", "Black or African American"),
            ("hispanic", "Hispanic"),
            ("caucasian", "White / Caucasian"),
            ("other", "Multiple ethnicity / Other (Please Specify)"),
            ("no-answer", "Prefer not to answer"),
        ],
        validators=[DataRequired()],
    )
    ethnicity_other = StringField(
        "Ethnicity (Please Specify)",
        validators=[DataRequiredIfOtherFieldEmpty("ethnicity")],
    )
    phone_number = StringField("Phone Number", validators=[DataRequired()])

    school = StringField("What school are you from?", validators=[DataRequired()])
    study_level = SelectField(
        "Level of Study",
        choices=[
            ("", ""),
            ("highschool", "High School"),
            ("undergraduate", "Undergraduate"),
            ("gradschool", "Graduate School"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    program = StringField("What program are you in?", validators=[DataRequired()])
    grad_year = IntegerField(
        "What is your expected graduation year?",
        validators=[
            DataRequired(),
            NumberRange(min=2000, max=2030, message="Please enter a realistic year"),
        ],
    )

    resume = FileField(
        "Upload your resume",
        validators=[Regexp(r"^.*\.(?:pdf|PDF)$", message="Resume must be a PDF")],
    )

    q1_prev_hackathon = TextAreaField(
        "Have you ever been to a hackathon/makeathon before? Tell us briefly about it",
        validators=[DataRequired()],
    )
    q2_why_participate = TextAreaField(
        "Why do you want to participate in MakeUofT?", validators=[DataRequired()]
    )
    q3_hardware_exp = TextAreaField(
        "Tell us about any experience you have with hardware!",
        validators=[DataRequired()],
    )

    how_you_hear = TextAreaField(
        "How did you hear about MakeUofT?", validators=[DataRequired()]
    )

    mlh_conduct = BooleanField("MLH Conduct", validators=[DataRequired()])
    mlh_data = BooleanField("MLH Data", validators=[DataRequired()])
    resume_share = BooleanField(
        "I consent to IEEE UofT sharing my resume with event sponsors"
    )
    age_confirmation = BooleanField(
        "I confirm that I will be 18 years of age or older and studying"
        "at a post-secondary institution on February 15, 2020"
    )

    submit = SubmitField("Register for MakeUofT 2020")


class ForgotPasswordEmailForm(FlaskForm):
    """
    Form takes email of contestant when they forgot their password
    """

    email = StringField("Email", validators=[DataRequired(), Email()])
