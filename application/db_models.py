from application import db
import uuid
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.inspection import inspect
from flask import jsonify

# Import class to provide functions for login of admins
from flask_login import UserMixin
from application import login_manager

# Import class to create and check password hashes
from werkzeug.security import generate_password_hash, check_password_hash

import datetime


def _generate_uuid():
    return uuid.uuid4().hex


class SerializerMixin:
    @staticmethod
    def _parse(val):
        if isinstance(val, datetime.datetime):
            return val.strftime("%Y-%m-%d %H:%M:%S")

        return val

    def serialize(self):
        column_attrs = inspect(self).mapper.column_attrs.keys()
        return {attr: self._parse(getattr(self, attr)) for attr in column_attrs}

    def json(self):
        return jsonify(self.serialize())


class MailingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)

    def __repr__(self):
        return "<Email {}>".format(self.id)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return "<Role {} | {}>".format(self.id, self.name)


class User(SerializerMixin, UserMixin, db.Model):
    # Define the columns of the table, including primary keys, unique, and
    # indexed fields, which makes searching faster
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(
        db.String(32), index=True, nullable=False, unique=True, default=_generate_uuid
    )
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

    roles = db.relationship("Role", secondary="user_roles", backref="users")

    def __repr__(self):
        return "<User {} | {} {}>".format(self.id, self.first_name, self.last_name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_allowed(self, page_role):
        if type(page_role) == list:
            for r in page_role:
                for available_role in self.roles:
                    if r == available_role.name:
                        return True
        else:
            for available_role in self.roles:
                if page_role == available_role.name:
                    return True
        return False

    @property
    def is_admin(self):
        return "admin" in [role.name for role in self.roles]

    def serialize(self):
        obj = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "id_provided": self.id_provided,
            "uuid": self.uuid,
            "status": self.application[0].status,
        }

        if self.team_id:
            obj["team_code"] = self.team.team_code

        return obj


class PasswordResets(db.Model):
    __tablename__ = "password_resets"
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship("User", backref="reset_token")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    token = db.Column(db.String(255), index=True, nullable=False)
    expiration = db.Column(DateTime(), server_default=func.now())


class UserRoles(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"))


def _generate_team_code():
    team_code = uuid.uuid4().hex[:5].upper()
    while db.session.query(Team.team_code).filter_by(team_code=team_code).count() > 0:
        team_code = uuid.uuid4().hex[:5].upper()

    return team_code


class Team(SerializerMixin, db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    team_code = db.Column(
        db.String(5), index=True, nullable=False, default=_generate_team_code
    )
    team_name = db.Column(db.String(255), nullable=True)
    created_time = db.Column(DateTime(), server_default=func.now())

    max_members = 4
    parts_used = db.relationship("PartsSignedOut", backref="team", lazy="dynamic")

    def __repr__(self):
        return "<Team {} | {}>".format(self.id, self.team_code)

    def serialize(self):
        obj = super().serialize()
        obj["members"] = [
            {"uuid": user.uuid,
             "first_name": user.first_name,
             "last_name": user.last_name,
             "status": user.application[0].status}
            for user in self.team_members
        ]
        return obj

    @property
    def submitted_time(self):
        submitted_time = (
            Team.query.join(User)
            .join(Application, Application.user_id == User.id)
            .group_by(Team.id)
            .having(Team.id == self.id)
            .with_entities(func.max(Application.submitted_time).label("submitted_time"))
            .first()
            .submitted_time
        )

        return submitted_time


class Application(SerializerMixin, db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    user = db.relationship(
        "User", foreign_keys=(user_id,), uselist=False, backref="application"
    )

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
    date_reviewed = db.Column(db.Date(), nullable=True)

    def __repr__(self):
        return "<Application {} | {} {}>".format(
            self.id, self.user.first_name, self.user.last_name
        )


tag_parts_available = db.Table(
    "tag_parts_available",
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
    db.Column(
        "part_id", db.Integer, db.ForeignKey("parts_available.id"), primary_key=True
    ),
)


class PartsAvailable(db.Model):
    # __tablename__ = 'parts_available'
    id = db.Column(db.Integer, primary_key=True)
    part_name = db.Column(db.String(255), index=True, nullable=False)
    part_manufacturer = db.Column(db.String(255), index=True)
    quantity_available = db.Column(db.Integer)
    quantity_remaining = db.Column(db.Integer)
    serial_number = db.Column(db.String(255))
    # ** Add tags relationship **
    # ** Add parts signed out relationship **
    parts_signed_out = db.relationship(
        "PartsSignedOut", backref="partsavailable", lazy=True
    )

    # Tags
    tag_list = db.relationship(
        "Tag",
        secondary=tag_parts_available,
        lazy="dynamic",
        backref=db.backref("partsavailable", lazy="dynamic"),
    )

    def __repr__(self):
        return "<Part {} | {}>".format(self.id, self.part_name)


class PartsSignedOut(db.Model):
    # __tablename__ = 'parts_signed_out'
    id = db.Column(db.Integer, primary_key=True)
    part_returned = db.Column(db.Boolean, default=False)
    part_healthy = db.Column(db.Boolean, default=False)
    created_date = db.Column(DateTime(), server_default=func.now())
    # ** Add PartsAvailable relationship **
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    # ** Add teams relationship **
    part_id = db.Column(db.Integer, db.ForeignKey("parts_available.id"))

    def __repr__(self):
        return "<Part {}>".format(self.id)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(255), index=True, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
