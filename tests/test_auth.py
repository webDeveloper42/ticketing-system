from ticketing import db
from ticketing.models import AuditLog


def test_login_success(login):
    response = login()
    assert response.status_code == 200
    assert b"Hello, Request" in response.data


def test_login_rejects_bad_password(login):
    response = login(password="wrong")
    assert b"Email or password is incorrect" in response.data


def test_protected_route_redirects(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_login_writes_audit_log(app, login):
    login()
    with app.app_context():
        assert db.session.query(AuditLog).filter_by(action="auth.login").count() == 1


def test_logout_is_post_only(client):
    assert client.get("/auth/logout").status_code == 405
