from flask import (
    request,
    render_template,
    flash,
    redirect,
    url_for,
)
from application.db_models import *
from application.auth.forms import (
    RegistrationForm,
    LoginForm,
    ForgotPasswordEmailForm,
    ChangePasswordForm,
)

from application import mail
from flask_mail import Message

# Import the admin Blueprint from admin/__init__.py
from application.auth import auth
from application import db
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
import secrets


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))

        # We set the `is_active` flag after email verification - force login prior to that
        # so that they can see pages saying to confirm their email
        login_user(user, remember=form.remember_me.data, force=True)
        next_page = request.args.get("next")

        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home.dashboard")

        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Send the verification email
        msg = Message("Activate your account for MakeUofT", recipients=[user.email])
        msg.html = render_template("mails/email-verification.html", user=user)
        mail.send(msg)

        return redirect(url_for("home.dashboard"))

    return render_template("auth/register.html", form=form)


@auth.route("/activate", methods=["GET"])
def activate():
    uuid = request.args.get("uuid", None)
    if not uuid:
        return "Missing uuid", 400

    user = User.query.filter_by(uuid=uuid).first_or_404("Invalid uuid")
    user.is_active = True

    db.session.commit()

    login_user(user, force=True)

    return redirect(url_for("home.dashboard"))


@auth.route("/changepassword", methods=["GET", "POST"])
@login_required
def change_password():
    """
    For when user is logged in and needs to change their password
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        user.set_password(form.password.data)
        db.session.commit()

        return render_template("auth/password_change_complete.html")

    return render_template("auth/update_password_form.html", form=form)


@auth.route("/forgotpassword", methods=["GET", "POST"])
def forgot_password():
    """
    User is logged out, does not remember their password, so we send them an email
    """
    if current_user.is_authenticated:
        return redirect(url_for("auth.change_password"))

    form = ForgotPasswordEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = secrets.token_urlsafe(32)  # Generate token
            reset_request = PasswordResets(
                user=user,
                token=token,
                expiration=datetime.now() + timedelta(minutes=30),
            )
            db.session.add(reset_request)
            db.session.commit()

            # Send the verification email
            msg = Message("MakeUofT Account Password Reset", recipients=[user.email])
            msg.html = render_template(
                "mails/reset-password.html", user=user, token=token
            )
            mail.send(msg)

        return render_template("auth/forgot_password_email_sent.html", email=form.email.data)

    return render_template("auth/forgotPasswordEnterEmail.html", form=form)


@auth.route("/resetpassword", methods=["GET"])
def reset_password():
    """
    User has received a password reset link from the forgot_password() function
    takes them here
    """
    token = request.args.get("token")
    if not token:
        return "Missing token", 400

    reset_request = PasswordResets.query.filter_by(token=token).first_or_404(
        "Invalid token"
    )

    if reset_request is not None and reset_request.expiration > datetime.now():
        login_user(reset_request.user, force=True)
        reset_request.expiration = datetime.now()
        db.session.commit()
        return redirect(url_for("auth.change_password"))

    return redirect(url_for("home.index"))
