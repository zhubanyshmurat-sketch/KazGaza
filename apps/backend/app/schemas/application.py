from datetime import date, datetime

from pydantic import BaseModel, Field

from kazgaza_shared import ApplicationPriority, ApplicationStatus, ApplicationType, FileType
from app.schemas.user import UserOut
from app.schemas.admin import AdminOut


class ApplicationPhotoIn(BaseModel):
    file_type: FileType
    telegram_file_id: str


class ApplicationCreateBot(BaseModel):
    telegram_user_id: int
    personal_account: str = Field(min_length=4, max_length=32)
    application_type: ApplicationType
    requested_date: date | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    photos: list[ApplicationPhotoIn] = Field(default_factory=list)


class FileOut(BaseModel):
    id: int
    file_type: FileType
    storage_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryOut(BaseModel):
    id: int
    old_status: ApplicationStatus | None
    new_status: ApplicationStatus
    comment: str | None
    admin: AdminOut | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationListItem(BaseModel):
    id: int
    application_number: str
    personal_account: str
    application_type: ApplicationType
    status: ApplicationStatus
    priority: ApplicationPriority
    created_at: datetime
    user: UserOut
    assigned_admin: AdminOut | None

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    items: list[ApplicationListItem]
    total: int
    page: int
    page_size: int


class ApplicationDetail(BaseModel):
    id: int
    application_number: str
    personal_account: str
    application_type: ApplicationType
    status: ApplicationStatus
    priority: ApplicationPriority
    requested_date: date | None
    latitude: float | None
    longitude: float | None
    admin_comment: str | None
    created_at: datetime
    updated_at: datetime
    user: UserOut
    assigned_admin: AdminOut | None
    files: list[FileOut]
    history: list[HistoryOut]

    model_config = {"from_attributes": True}


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    comment: str | None = Field(default=None, max_length=2000)


class ApplicationAssignUpdate(BaseModel):
    assigned_to: int | None


class ApplicationCommentCreate(BaseModel):
    comment: str = Field(min_length=1, max_length=2000)


class ApplicationUpdate(BaseModel):
    admin_comment: str | None = Field(default=None, max_length=2000)
    priority: ApplicationPriority | None = None


class BotApplicationSummary(BaseModel):
    application_number: str
    application_type: ApplicationType
    status: ApplicationStatus
    created_at: datetime

    model_config = {"from_attributes": True}
