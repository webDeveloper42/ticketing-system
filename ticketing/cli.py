import os

import click
from flask.cli import with_appcontext
from sqlalchemy import select

from ticketing import db
from ticketing.models import Priority, Role, Ticket, User
from ticketing.services import TicketService


def register_commands(app):
    @app.cli.command("init-db")
    @with_appcontext
    def init_db():
        db.create_all()
        click.echo("Database tables are ready.")

    @app.cli.command("seed-demo")
    @with_appcontext
    def seed_demo():
        db.create_all()
        users = [
            (
                "Administrator",
                os.getenv("ADMIN_EMAIL", "admin@example.com"),
                os.getenv("ADMIN_PASSWORD", "ChangeMe123!"),
                Role.ADMIN,
            ),
            ("Alex Agent", "agent@example.com", "Agent123!", Role.AGENT),
            ("Riley Requester", "requester@example.com", "Requester123!", Role.REQUESTER),
        ]
        made = {}
        for name, email, password, role in users:
            user = db.session.scalar(select(User).where(User.email == email))
            if not user:
                user = User(name=name, email=email, role=role)
                user.set_password(password)
                db.session.add(user)
            made[role] = user
        db.session.commit()
        if not db.session.scalar(select(Ticket).limit(1)):
            TicketService.create(
                requester=made[Role.REQUESTER],
                title="Laptop cannot connect to office Wi-Fi",
                description=(
                    "Connection drops after authentication. Restarting the laptop "
                    "did not resolve it."
                ),
                category="network",
                priority=Priority.HIGH,
            )
            TicketService.create(
                requester=made[Role.REQUESTER],
                title="Request access to shared finance folder",
                description="I need read-only access to prepare the weekly operations report.",
                category="access",
                priority=Priority.MEDIUM,
            )
        click.echo("Demo users and tickets are ready.")
