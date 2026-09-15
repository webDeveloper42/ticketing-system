from ticketing import db
from ticketing.models import AuditLog, Comment, Ticket, TicketStatus


def test_requester_creates_ticket(app, login, client):
    login()
    response = client.post(
        "/tickets/new",
        data={
            "title": "VPN login fails repeatedly",
            "category": "network",
            "priority": "high",
            "description": "The VPN rejects valid credentials after a password reset.",
        },
        follow_redirects=True,
    )
    assert b"was created" in response.data
    with app.app_context():
        assert db.session.query(Ticket).count() == 2
        assert db.session.query(AuditLog).filter_by(action="ticket.created").count() == 1


def test_validation_rejects_short_ticket(login, client):
    login()
    response = client.post(
        "/tickets/new",
        data={"title": "Bad", "category": "general", "priority": "low", "description": "too short"},
    )
    assert response.status_code == 200
    assert b"between 5 and 160 characters" in response.data


def test_requester_cannot_see_another_users_ticket(app, login, client):
    with app.app_context():
        from ticketing.models import User

        other = db.session.query(User).filter_by(email="other@example.com").one()
        ticket = Ticket(
            title="Private account issue",
            description="This request belongs to another requester account.",
            requester=other,
        )
        db.session.add(ticket)
        db.session.commit()
        ticket_id = ticket.id
    login()
    assert client.get(f"/tickets/{ticket_id}").status_code == 404


def test_requester_cannot_manage_ticket(login, client):
    login()
    assert client.get("/tickets/1/manage").status_code == 403


def test_agent_can_manage_and_assign(app, login, client):
    login("agent@example.com", "Agent123!")
    with app.app_context():
        from ticketing.models import User

        agent_id = db.session.query(User).filter_by(email="agent@example.com").one().id
    response = client.post(
        "/tickets/1/manage",
        data={"status": "in_progress", "priority": "high", "assignee_id": agent_id},
        follow_redirects=True,
    )
    assert b"Ticket updated" in response.data
    with app.app_context():
        ticket = db.session.get(Ticket, 1)
        assert ticket.status == TicketStatus.IN_PROGRESS
        assert ticket.assignee_id == agent_id


def test_public_comment_visible_to_requester(app, login, client):
    login("agent@example.com", "Agent123!")
    client.post(
        "/tickets/1",
        data={"body": "Please restart the printer and try one test page.", "internal": ""},
    )
    client.post("/auth/logout")
    login()
    response = client.get("/tickets/1")
    assert b"Please restart the printer" in response.data


def test_internal_comment_hidden_from_requester(app, login, client):
    login("agent@example.com", "Agent123!")
    client.post("/tickets/1", data={"body": "Suspect failing imaging drum.", "internal": "y"})
    with app.app_context():
        assert db.session.query(Comment).filter_by(internal=True).count() == 1
    client.post("/auth/logout")
    login()
    response = client.get("/tickets/1")
    assert b"Suspect failing imaging drum" not in response.data


def test_filters_ticket_queue(login, client):
    login("agent@example.com", "Agent123!")
    assert b"Printer produces" in client.get("/tickets?priority=medium").data
    assert b"Printer produces" not in client.get("/tickets?priority=critical").data
