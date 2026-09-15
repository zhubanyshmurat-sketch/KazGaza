from pydantic import BaseModel


class DashboardStats(BaseModel):
    total: int
    new: int
    in_progress: int
    completed: int
    rejected: int
    critical: int
    by_type: dict[str, int]
    by_day: list[dict[str, int | str]]


class ReportStats(BaseModel):
    total: int
    new: int
    in_progress: int
    completed: int
    rejected: int
    critical: int
    avg_processing_hours: float | None


class SettingsOut(BaseModel):
    organization_name: str
    contact_phone: str
    emergency_phone: str
    max_photo_size_mb: int
    welcome_text: str
    status_new_text: str
    status_in_progress_text: str
    status_completed_text: str
    status_rejected_text: str

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    organization_name: str | None = None
    contact_phone: str | None = None
    emergency_phone: str | None = None
    max_photo_size_mb: int | None = None
    welcome_text: str | None = None
    status_new_text: str | None = None
    status_in_progress_text: str | None = None
    status_completed_text: str | None = None
    status_rejected_text: str | None = None
