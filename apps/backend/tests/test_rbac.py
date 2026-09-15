import pytest

from tests.conftest import login

pytestmark = pytest.mark.asyncio


async def test_operator_cannot_create_admin(client, operator_admin):
    await login(client, "operator@kazgaza.kz", "operator123")
    resp = await client.post(
        "/api/v1/admins",
        json={"name": "New", "email": "new@kazgaza.kz", "password": "password123", "role": "OPERATOR"},
    )
    assert resp.status_code == 403


async def test_super_admin_can_create_admin(client, super_admin):
    await login(client, "super@kazgaza.kz", "supersecret123")
    resp = await client.post(
        "/api/v1/admins",
        json={"name": "New Op", "email": "newop@kazgaza.kz", "password": "password123", "role": "OPERATOR"},
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "OPERATOR"


async def test_operator_cannot_assign_application(client, operator_admin):
    await login(client, "operator@kazgaza.kz", "operator123")
    resp = await client.patch("/api/v1/applications/1/assign", json={"assigned_to": None})
    assert resp.status_code == 403


async def test_operator_can_read_dashboard_stats(client, operator_admin):
    await login(client, "operator@kazgaza.kz", "operator123")
    resp = await client.get("/api/v1/dashboard/stats")
    assert resp.status_code == 200


async def test_operator_can_read_report(client, operator_admin):
    await login(client, "operator@kazgaza.kz", "operator123")
    resp = await client.get("/api/v1/dashboard/report")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["avg_processing_hours"] is None


async def test_dispatcher_can_list_admins_but_not_create(client, dispatcher_admin):
    await login(client, "dispatcher@kazgaza.kz", "dispatcher123")
    resp = await client.get("/api/v1/admins")
    assert resp.status_code == 200

    resp = await client.post(
        "/api/v1/admins",
        json={"name": "X", "email": "x@kazgaza.kz", "password": "password123", "role": "OPERATOR"},
    )
    assert resp.status_code == 403


async def test_operator_cannot_list_admins(client, operator_admin):
    await login(client, "operator@kazgaza.kz", "operator123")
    resp = await client.get("/api/v1/admins")
    assert resp.status_code == 403
