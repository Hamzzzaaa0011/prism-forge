from app.models import User


def test_register_creates_and_logs_in_user(client):
    response = client.post(
        "/auth/register",
        data={
            "email": "maya@example.com",
            "username": "maya",
            "password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert User.query.filter_by(email="maya@example.com").one()
    assert b"Put the idea under pressure" in response.data


def test_duplicate_registration_shows_error(client):
    payload = {
        "email": "maya@example.com",
        "username": "maya",
        "password": "password123",
    }
    client.post("/auth/register", data=payload)
    client.post("/auth/logout")
    response = client.post("/auth/register", data=payload, follow_redirects=True)

    assert b"already in use" in response.data


def test_login_rejects_wrong_password(client):
    client.post(
        "/auth/register",
        data={
            "email": "maya@example.com",
            "username": "maya",
            "password": "password123",
        },
    )
    client.post("/auth/logout")
    response = client.post(
        "/auth/login",
        data={"email": "maya@example.com", "password": "wrong-pass"},
        follow_redirects=True,
    )

    assert b"Invalid email or password" in response.data
