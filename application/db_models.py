from application import db
import datetime
from sqlalchemy import DateTime
from sqlalchemy.sql import func

# Import class to provide functions for login of admins
from flask_login import UserMixin
from application import login_manager

# Import class to create and check password hashes
from werkzeug.security import generate_password_hash, check_password_hash


class MailingList(db.Model):
    __tablename__ = "MailingList"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)

    def __repr__(self):
        return "<Email {}>".format(self.id)


class User(UserMixin, db.Model):
    # Define the columns of the table, including primary keys, unique, and
    # indexed fields, which makes searching faster
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), index=True, nullable=False)
    last_name = db.Column(db.String(255), index=True, nullable=False)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_date = db.Column(
        DateTime(), server_default=func.now()
    )  # func.now() tells the db to calculate the timestamp itself rather than letting the application do it
    updated_date = db.Column(DateTime(), onupdate=func.now())

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="SET NULL"))
    team = db.relationship("Team", backref="team_members")
    application = db.relationship("Application", uselist=False, backref="user")

    def __repr__(self):
        return "<User {}>".format(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    team_code = db.Column(db.String(5), index=True, nullable=False)
    created_time = db.Column(DateTime(), server_default=func.now())


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)

    # User submitted fields
    preferred_name = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date(), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    ethnicity = db.Column(db.String(255), nullable=False)
    tshirt_size = db.Column(db.String(5), nullable=False)
    dietary_restrictions = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=False)
    school = db.Column(db.String(255), nullable=False)
    study_level = db.Column(db.String(16), nullable=False)
    program = db.Column(db.String(255), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    resume_path = db.Column(db.String(255), nullable=False)
    q1_prev_hackathon = db.Column(db.Text(1000), nullable=False)
    q2_why_participate = db.Column(db.Text(1000), nullable=False)
    q3_hardware_exp = db.Column(db.Text(1000), nullable=False)
    referral_source = db.Column(db.Text(255), nullable=False)
    mlh_conduct_agree = db.Column(db.Boolean(), nullable=False, default=False)
    mlh_data_agree = db.Column(db.Boolean(), nullable=False, default=False)
    resume_sharing = db.Column(db.Boolean(), nullable=False, default=False)
    age_confirmation = db.Column(db.Boolean(), nullable=False, default=False)
    submitted_time = db.Column(db.DateTime(), server_default=func.now())

    # Reviewer fields
    status = db.Column(db.String(64), default=None, nullable=True)
    evaluator = db.Column(
        db.Integer, db.ForeignKey("users.id"), default=None, nullable=True
    )
    evaluator_comments = db.Column(db.Text(255), nullable=True)
    experience = db.Column(db.Integer, nullable=True)
    interest = db.Column(db.Integer, nullable=True)
    quality = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return "<Application {} | {} {}>".format(
            self.id, self.user.first_name, self.user.last_name
        )


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
