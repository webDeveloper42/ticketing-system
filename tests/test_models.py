from datetime import timedelta

from ticketing import db
from ticketing.models import Priority, Ticket


def test_password_hash_is_not_plaintext(app):
    from ticketing.models import User

    with app.app_context():
        user = db.session.query(User).filter_by(email="request@example.com").one()
        assert "Request123!" not in user.password_hash
        assert user.check_password("Request123!")


def test_ticket_reference_and_sla(app):
    with app.app_context():
        ticket = db.session.query(Ticket).first()
        assert ticket.reference == "TKT-00001"
        assert ticket.sla_due_at == ticket.created_at + timedelta(hours=24)


def test_priority_sla_windows(app):
    with app.app_context():
        ticket = db.session.query(Ticket).first()
        expected = {Priority.CRITICAL: 4, Priority.HIGH: 8, Priority.MEDIUM: 24, Priority.LOW: 72}
        for priority, hours in expected.items():
            ticket.priority = priority
            assert ticket.sla_due_at == ticket.created_at + timedelta(hours=hours)
