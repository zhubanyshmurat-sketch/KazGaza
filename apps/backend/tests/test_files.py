import io

import pytest
from fastapi import HTTPException
from PIL import Image

from app.services import file_service


def _make_jpeg_bytes(size=(100, 100)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color="red").save(buf, format="JPEG")
    return buf.getvalue()


def test_validate_and_identify_image_accepts_jpeg():
    raw = _make_jpeg_bytes()
    mime = file_service.validate_and_identify_image(raw)
    assert mime == "image/jpeg"


def test_validate_and_identify_image_rejects_non_image():
    with pytest.raises(HTTPException) as exc_info:
        file_service.validate_and_identify_image(b"not an image, just plain text bytes")
    assert exc_info.value.status_code == 400


def test_validate_and_identify_image_rejects_oversized(monkeypatch):
    monkeypatch.setattr(file_service.settings, "MAX_UPLOAD_MB", 0)
    raw = _make_jpeg_bytes()
    with pytest.raises(HTTPException) as exc_info:
        file_service.validate_and_identify_image(raw)
    assert exc_info.value.status_code == 413


def test_store_image_writes_file_under_application_number(tmp_path, monkeypatch):
    monkeypatch.setattr(file_service.settings, "UPLOAD_DIR", str(tmp_path))
    raw = _make_jpeg_bytes()
    url = file_service.store_image(raw, "image/jpeg", "REQ-20260915-00001")
    assert "REQ-20260915-00001" in url
    stored_files = list((tmp_path / "REQ-20260915-00001").iterdir())
    assert len(stored_files) == 1
    assert stored_files[0].read_bytes() == raw


def test_required_photos_per_application_type():
    from kazgaza_shared import FileType

    assert file_service.REQUIRED_PHOTOS["METER_NOT_WORKING"] == {FileType.METER_PHOTO}
    assert file_service.REQUIRED_PHOTOS["GAS_LEAK"] == {FileType.METER_PHOTO, FileType.GAS_LEAK_PHOTO}
    assert file_service.REQUIRED_PHOTOS["MPI_REMOVAL"] == set()
