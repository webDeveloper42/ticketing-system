import pytest

from ticketing import create_app, db
from ticketing.models import Priority, Role, Ticket, User


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": "test-secret",
        }
    )
    with app.app_context():
        db.create_all()
        requester = User(name="Request User", email="request@example.com", role=Role.REQUESTER)
        requester.set_password("Request123!")
        other = User(name="Other User", email="other@example.com", role=Role.REQUESTER)
        other.set_password("Other123!")
        agent = User(name="Agent User", email="agent@example.com", role=Role.AGENT)
        agent.set_password("Agent123!")
        admin = User(name="Admin User", email="admin@example.com", role=Role.ADMIN)
        admin.set_password("Admin123!")
        db.session.add_all([requester, other, agent, admin])
        db.session.commit()
        ticket = Ticket(
            title="Printer produces blank pages",
            description="The third floor printer produces blank pages after toner replacement.",
            category="hardware",
            priority=Priority.MEDIUM,
            requester=requester,
        )
        db.session.add(ticket)
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def do_login(email="request@example.com", password="Request123!"):
        return client.post(
            "/auth/login", data={"email": email, "password": password}, follow_redirects=True
        )

    return do_login
