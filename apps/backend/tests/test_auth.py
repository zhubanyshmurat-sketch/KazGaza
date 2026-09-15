import pytest

pytestmark = pytest.mark.asyncio


async def test_login_success_sets_cookies_and_csrf(client, super_admin):
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "super@kazgaza.kz", "password": "supersecret123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["admin"]["email"] == "super@kazgaza.kz"
    assert body["csrf_token"]
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


async def test_login_wrong_password_rejected(client, super_admin):
    resp = await client.post("/api/v1/auth/login", json={"email": "super@kazgaza.kz", "password": "wrong"})
    assert resp.status_code == 401


async def test_login_inactive_admin_rejected(client, super_admin, db_session):
    super_admin.active = False
    db_session.add(super_admin)
    await db_session.commit()
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "super@kazgaza.kz", "password": "supersecret123"}
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_admin(client, super_admin):
    from tests.conftest import login

    await login(client, "super@kazgaza.kz", "supersecret123")
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "super@kazgaza.kz"


async def test_mutating_request_without_csrf_header_rejected(client, super_admin):
    resp = await client.post("/api/v1/auth/login", json={"email": "super@kazgaza.kz", "password": "supersecret123"})
    assert resp.status_code == 200
    client.headers.pop("X-CSRF-Token", None)
    resp = await client.patch("/api/v1/settings", json={"contact_phone": "+7 700 000 00 00"})
    assert resp.status_code == 403
