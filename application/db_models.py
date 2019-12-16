from application import db
import datetime
import uuid
from sqlalchemy import DateTime
from sqlalchemy.sql import func

# Import class to provide functions for login of admins
from flask_login import UserMixin
from application import login_manager

# Import class to create and check password hashes
from werkzeug.security import generate_password_hash, check_password_hash


def _generate_uuid():
    return uuid.uuid4().hex


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
    uuid = db.Column(db.String(32), index=True, nullable=False, unique=True, default=_generate_uuid)
    first_name = db.Column(db.String(255), index=True, nullable=False)
    last_name = db.Column(db.String(255), index=True, nullable=False)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    is_active = db.Column(db.Boolean(), nullable=False, default=False)
    password_hash = db.Column(db.String(128))
    created_date = db.Column(
        DateTime(), server_default=func.now()
    )  # func.now() tells the db to calculate the timestamp itself rather than letting the application do it
    updated_date = db.Column(DateTime(), onupdate=func.now())

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="SET NULL"))
    team = db.relationship("Team", backref="team_members")

    id_provided = db.Column(db.Boolean, default=False)

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
    team_name = db.Column(db.String(255))
    created_time = db.Column(DateTime(), server_default=func.now())

    max_members = 4
    parts_used = db.relationship('PartsSignedOut', backref='teams', lazy='dynamic')

    def __repr__(self):
        return '<Team {}>'.format(self.id) #prints <Team 'id'>


tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('part_id', db.Integer, db.ForeignKey('parts_available.id'), primary_key=True)
)

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    user = db.relationship("User", foreign_keys=(user_id,), uselist=False, backref="application")

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
    evaluator_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), default=None, nullable=True
    )
    evaluator = db.relationship("User", foreign_keys=(evaluator_id,))
    evaluator_comments = db.Column(db.Text(255), nullable=True)
    experience = db.Column(db.Integer, nullable=True)
    interest = db.Column(db.Integer, nullable=True)
    quality = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return "<Application {} | {} {}>".format(
            self.id, self.user.first_name, self.user.last_name
        )

class PartsAvailable(db.Model):
    #__tablename__ = 'parts_available'
    id = db.Column(db.Integer, primary_key=True)
    part_name = db.Column(db.String(255), index=True, nullable=False)
    part_manufacturer = db.Column(db.String(255), index=True)
    quantity_available = db.Column(db.Integer)
    quantity_remaining = db.Column(db.Integer)
    serial_number = db.Column(db.String(255))
    # ** Add tags relationship **
    # ** Add parts signed out relationship **
    parts_signed_out = db.relationship('PartsSignedOut', backref='partsavailable', lazy=True)

    # Tags
    tag_list = db.relationship('Tag', secondary=tags, lazy='dynamic',
        backref=db.backref('partsavailable', lazy='dynamic'))
    # __repr__ method describes how objects of this class are printed
    # (useful for debugging)



    def __repr__(self):
        return '<Part {}>'.format(self.id) #prints <Part 'id'>

class PartsSignedOut(db.Model):
    #__tablename__ = 'parts_signed_out'
    id = db.Column(db.Integer, primary_key=True)
    part_returned = db.Column(db.Boolean, default=False)
    part_healthy = db.Column(db.Boolean, default=False)
    created_date = db.Column(DateTime(), server_default=func.now()) #func.now() tells the db to calculate the timestamp itself rather than letting the application do it
    # ** Add PartsAvailable relationship **
    team = db.Column(db.Integer, db.ForeignKey('teams.id'))
    # ** Add teams relationship **
    part = db.Column(db.Integer, db.ForeignKey('parts_available.id'))


    # __repr__ method describes how objects of this class are printed
    # (useful for debugging)
    def __repr__(self):
        return '<Part {}>'.format(self.id) #prints <Part 'id'>

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(255), index=True, nullable=False)

# Many 2 many:
# https://www.reddit.com/r/flask/comments/6p359d/flask_sqlalchemy_many_to_many_xpost_rlearnpython/

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
