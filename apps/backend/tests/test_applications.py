import pytest

from tests.conftest import login

pytestmark = pytest.mark.asyncio

BOT_HEADERS = {"X-Bot-Secret": "test-bot-secret"}


async def _register_bot_user(client, telegram_user_id=111222333):
    resp = await client.post(
        "/api/v1/bot/users/register",
        json={"telegram_user_id": telegram_user_id, "telegram_username": "resident1", "first_name": "Ali"},
        headers=BOT_HEADERS,
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.fixture(autouse=True)
def mock_telegram(monkeypatch):
    async def fake_download_validate_store(telegram_file_id, application_number):
        return f"/media/{application_number}/{telegram_file_id}.jpg"

    sent_messages = []

    async def fake_send_telegram_message(telegram_user_id, text):
        sent_messages.append((telegram_user_id, text))

    monkeypatch.setattr(
        "app.services.application_service.file_service.download_validate_store",
        fake_download_validate_store,
    )
    monkeypatch.setattr(
        "app.services.application_service.send_telegram_message", fake_send_telegram_message
    )
    return sent_messages


async def test_bot_endpoints_require_secret(client):
    resp = await client.post("/api/v1/bot/users/register", json={"telegram_user_id": 1})
    assert resp.status_code == 401


async def test_create_meter_not_working_application(client):
    await _register_bot_user(client)
    resp = await client.post(
        "/api/v1/bot/applications",
        json={
            "telegram_user_id": 111222333,
            "personal_account": "123456789",
            "application_type": "METER_NOT_WORKING",
            "latitude": 51.169,
            "longitude": 71.449,
            "photos": [{"file_type": "METER_PHOTO", "telegram_file_id": "file123"}],
        },
        headers=BOT_HEADERS,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["application_number"].startswith("REQ-")


async def test_create_meter_application_without_photo_rejected(client):
    await _register_bot_user(client)
    resp = await client.post(
        "/api/v1/bot/applications",
        json={
            "telegram_user_id": 111222333,
            "personal_account": "123456789",
            "application_type": "METER_NOT_WORKING",
            "latitude": 51.169,
            "longitude": 71.449,
            "photos": [],
        },
        headers=BOT_HEADERS,
    )
    assert resp.status_code == 400


async def test_create_mpi_application_requires_date(client):
    await _register_bot_user(client)
    resp = await client.post(
        "/api/v1/bot/applications",
        json={
            "telegram_user_id": 111222333,
            "personal_account": "123456789",
            "application_type": "MPI_REMOVAL",
            "photos": [],
        },
        headers=BOT_HEADERS,
    )
    assert resp.status_code == 400

    resp = await client.post(
        "/api/v1/bot/applications",
        json={
            "telegram_user_id": 111222333,
            "personal_account": "123456789",
            "application_type": "MPI_REMOVAL",
            "requested_date": "2026-09-25",
            "photos": [],
        },
        headers=BOT_HEADERS,
    )
    assert resp.status_code == 200


async def test_gas_leak_application_gets_critical_priority(client, super_admin):
    await _register_bot_user(client)
    resp = await client.post(
        "/api/v1/bot/applications",
        json={
            "telegram_user_id": 111222333,
            "personal_account": "123456789",
            "application_type": "GAS_LEAK",
            "latitude": 51.169,
            "longitude": 71.449,
            "photos": [
                {"file_type": "METER_PHOTO", "telegram_file_id": "meter1"},
                {"file_type": "GAS_LEAK_PHOTO", "telegram_file_id": "leak1"},
            ],
        },
        headers=BOT_HEADERS,
    )
    assert resp.status_code == 200, resp.text
    application_id = resp.json()["id"]

    await login(client, "super@kazgaza.kz", "supersecret123")
    detail = await client.get(f"/api/v1/applications/{application_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["priority"] == "CRITICAL"
    assert {f["file_type"] for f in body["files"]} == {"METER_PHOTO", "GAS_LEAK_PHOTO"}


async def test_gas_leak_without_both_photos_rejected(client):
    await _register_bot_user(client)
    resp = await client.post(
        "/api/v1/bot/applications",
        json={
            "telegram_user_id": 111222333,
            "personal_account": "123456789",
            "application_type": "GAS_LEAK",
            "latitude": 51.169,
            "longitude": 71.449,
            "photos": [{"file_type": "METER_PHOTO", "telegram_file_id": "meter1"}],
        },
        headers=BOT_HEADERS,
    )
    assert resp.status_code == 400


async def test_status_change_notifies_user_and_logs_history(client, super_admin, mock_telegram):
    await _register_bot_user(client)
    create_resp = await client.post(
        "/api/v1/bot/applications",
        json={
            "telegram_user_id": 111222333,
            "personal_account": "123456789",
            "application_type": "METER_NOT_WORKING",
            "latitude": 51.169,
            "longitude": 71.449,
            "photos": [{"file_type": "METER_PHOTO", "telegram_file_id": "file123"}],
        },
        headers=BOT_HEADERS,
    )
    application_id = create_resp.json()["id"]

    await login(client, "super@kazgaza.kz", "supersecret123")
    resp = await client.patch(
        f"/api/v1/applications/{application_id}/status",
        json={"status": "IN_PROGRESS", "comment": "Қабылданды"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "IN_PROGRESS"

    assert len(mock_telegram) == 1
    telegram_user_id, text = mock_telegram[0]
    assert telegram_user_id == 111222333
    assert "REQ-" in text

    history_resp = await client.get(f"/api/v1/applications/{application_id}/history")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) == 2  # creation + status change
    assert history[-1]["new_status"] == "IN_PROGRESS"
    assert history[-1]["old_status"] == "NEW"


async def test_my_applications_returns_only_own_applications(client):
    await _register_bot_user(client, telegram_user_id=1)
    await _register_bot_user(client, telegram_user_id=2)

    await client.post(
        "/api/v1/bot/applications",
        json={
            "telegram_user_id": 1,
            "personal_account": "123456789",
            "application_type": "METER_NOT_WORKING",
            "latitude": 51.0,
            "longitude": 71.0,
            "photos": [{"file_type": "METER_PHOTO", "telegram_file_id": "f1"}],
        },
        headers=BOT_HEADERS,
    )

    resp = await client.get("/api/v1/bot/applications/mine", params={"telegram_user_id": 1}, headers=BOT_HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp2 = await client.get("/api/v1/bot/applications/mine", params={"telegram_user_id": 2}, headers=BOT_HEADERS)
    assert resp2.status_code == 200
    assert resp2.json() == []
