from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import select

from ticketing import db
from ticketing.forms import LoginForm
from ticketing.models import AuditLog, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.email == form.email.data.lower().strip()))
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user)
            db.session.add(
                AuditLog(actor=user, action="auth.login", ip_address=request.remote_addr)
            )
            db.session.commit()
            return redirect(url_for("main.dashboard"))
        flash("Email or password is incorrect.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.post("/logout")
def logout():
    if current_user.is_authenticated:
        db.session.add(
            AuditLog(actor=current_user, action="auth.logout", ip_address=request.remote_addr)
        )
        db.session.commit()
    logout_user()
    return redirect(url_for("auth.login"))
