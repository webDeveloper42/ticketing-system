import re


def test_security_headers(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_post_without_csrf_rejected_when_enabled():
    from ticketing import create_app, db

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": "csrf-test",
            "WTF_CSRF_ENABLED": True,
        }
    )
    with app.app_context():
        db.create_all()
    response = app.test_client().post(
        "/auth/login", data={"email": "x@y.com", "password": "password"}
    )
    assert response.status_code == 400


def test_login_accepts_valid_csrf_token():
    from ticketing import create_app, db
    from ticketing.models import Role, User

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": "csrf-test",
            "WTF_CSRF_ENABLED": True,
        }
    )
    with app.app_context():
        db.create_all()
        user = User(name="CSRF User", email="csrf@example.com", role=Role.REQUESTER)
        user.set_password("Request123!")
        db.session.add(user)
        db.session.commit()

    client = app.test_client()
    login_page = client.get("/auth/login")
    match = re.search(rb'name="csrf_token"[^>]*value="([^"]+)"', login_page.data)
    assert match is not None

    response = client.post(
        "/auth/login",
        data={
            "csrf_token": match.group(1).decode(),
            "email": "csrf@example.com",
            "password": "Request123!",
        },
    )
    assert response.status_code == 302
    assert response.location.endswith("/dashboard")


def test_oversized_request_rejected(app, client):
    response = client.post("/auth/login", data={"email": "a" * (2 * 1024 * 1024), "password": "x"})
    assert response.status_code == 413


def test_sql_injection_string_does_not_authenticate(login):
    response = login("' OR 1=1 --", "anything")
    assert (
        b"Email or password is incorrect" in response.data
        or b"Invalid email address" in response.data
    )
