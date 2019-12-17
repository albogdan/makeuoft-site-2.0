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
)

from application import mail
from flask_mail import Message

# Import the admin Blueprint from admin/__init__.py
from application.auth import auth
from application import db
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse


@auth.route("/login", methods=["GET", "POST"])
# ADD FLASH MESSAGES WHEN THEY GET INCORRECT LOGIN
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")

        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home.index")

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
        print("Submission successful")
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


@auth.route("/activate", methods=("GET",))
def activate():
    uuid = request.args.get("uuid", None)
    if not request.uuid:
        return "Missing uuid", 400

    user = db.session.query(User).filter_by(uuid=uuid).first()
    if not user:
        return "Invalid uuid", 404

    user.is_active = True
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("home.dashboard"))


@auth.route("/passwordupdated", methods=["GET", "POST"])
def passwordChangeComplete():
    return render_template("auth/forgotPasswordChangeComplete.html")


@auth.route("/forgotpassword", methods=["GET", "POST"])
def forgotPassword():
    form = ForgotPasswordEmailForm()
    return render_template("auth/forgotPasswordEnterEmail.html", form=form)


@auth.route("/newpassword", methods=["GET", "POST"])
def newPassword():
    return render_template("auth/forgotPasswordEnterNewPassword.html")


@auth.route("/confirmemail", methods=["GET", "POST"])
def confirmEmail():
    return render_template("auth/signupEmailToConfirm.html")


@auth.route("/emailconfirmed", methods=["GET", "POST"])
def emailConfirmed():
    return render_template("auth/signupEmailConfirmed.html")
