from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length

from ticketing.models import Priority, TicketStatus


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Sign in")


class TicketForm(FlaskForm):
    title = StringField("Short summary", validators=[DataRequired(), Length(min=5, max=160)])
    category = SelectField(
        "Category",
        choices=[
            ("hardware", "Hardware"),
            ("software", "Software"),
            ("access", "Account / access"),
            ("network", "Network"),
            ("general", "Other"),
        ],
    )
    priority = SelectField("Impact", choices=[(p.value, p.value.title()) for p in Priority])
    description = TextAreaField(
        "What happened?", validators=[DataRequired(), Length(min=10, max=5000)]
    )
    submit = SubmitField("Create ticket")


class CommentForm(FlaskForm):
    body = TextAreaField("Reply", validators=[DataRequired(), Length(min=2, max=5000)])
    internal = BooleanField("Internal note (staff only)")
    submit = SubmitField("Add update")


class UpdateTicketForm(FlaskForm):
    status = SelectField(
        "Status", choices=[(s.value, s.value.replace("_", " ").title()) for s in TicketStatus]
    )
    priority = SelectField("Priority", choices=[(p.value, p.value.title()) for p in Priority])
    assignee_id = SelectField("Assignee", coerce=int)
    submit = SubmitField("Save changes")
