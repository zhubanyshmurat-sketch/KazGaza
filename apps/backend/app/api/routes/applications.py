from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db
from app.auth.rbac import require_any_admin, require_dispatcher_or_above
from app.models.admin import Admin
from app.repositories import application_repo
from app.schemas.application import (
    ApplicationAssignUpdate,
    ApplicationCommentCreate,
    ApplicationDetail,
    ApplicationListResponse,
    ApplicationStatusUpdate,
    ApplicationUpdate,
    HistoryOut,
)
from app.services import application_service, export_service
from kazgaza_shared import ApplicationPriority, ApplicationStatus, ApplicationType

router = APIRouter(prefix="/applications", tags=["applications"])


async def _get_or_404(db: AsyncSession, application_id: int):
    application = await application_repo.get_by_id(db, application_id)
    if not application:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Өтінім табылмады.")
    return application


@router.get("", response_model=ApplicationListResponse, dependencies=[Depends(require_any_admin)])
async def list_applications(
    db: AsyncSession = Depends(get_db),
    application_number: str | None = None,
    personal_account: str | None = None,
    application_type: ApplicationType | None = None,
    status_: ApplicationStatus | None = Query(default=None, alias="status"),
    priority: ApplicationPriority | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    q: str | None = None,
    sort: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    items, total = await application_repo.search(
        db,
        application_number=application_number,
        personal_account=personal_account,
        application_type=application_type,
        status=status_,
        priority=priority,
        date_from=date_from,
        date_to=date_to,
        query=q,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    return ApplicationListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/export", dependencies=[Depends(require_any_admin)])
async def export_applications(
    db: AsyncSession = Depends(get_db),
    format: str = Query(default="xlsx", pattern="^(csv|xlsx)$"),
    application_type: ApplicationType | None = None,
    status_: ApplicationStatus | None = Query(default=None, alias="status"),
    priority: ApplicationPriority | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    items, _ = await application_repo.search(
        db,
        application_type=application_type,
        status=status_,
        priority=priority,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10_000,
    )
    if format == "csv":
        content = export_service.export_csv(items)
        media_type = "text/csv"
        filename = "applications.csv"
    else:
        content = export_service.export_xlsx(items)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "applications.xlsx"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{application_id}", response_model=ApplicationDetail, dependencies=[Depends(require_any_admin)])
async def get_application(application_id: int, db: AsyncSession = Depends(get_db)):
    return await _get_or_404(db, application_id)


@router.patch("/{application_id}", response_model=ApplicationDetail, dependencies=[Depends(require_any_admin)])
async def update_application(application_id: int, data: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    application = await _get_or_404(db, application_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    await db.commit()
    return await application_repo.get_by_id(db, application_id)


@router.patch(
    "/{application_id}/status", response_model=ApplicationDetail, dependencies=[Depends(require_any_admin)]
)
async def update_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    application = await _get_or_404(db, application_id)
    return await application_service.change_status(db, application, data.status, data.comment, admin)


@router.patch(
    "/{application_id}/assign",
    response_model=ApplicationDetail,
    dependencies=[Depends(require_dispatcher_or_above)],
)
async def assign_application(
    application_id: int,
    data: ApplicationAssignUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    application = await _get_or_404(db, application_id)
    return await application_service.assign_application(db, application, data.assigned_to, admin)


@router.post(
    "/{application_id}/comments", response_model=ApplicationDetail, dependencies=[Depends(require_any_admin)]
)
async def add_comment(
    application_id: int,
    data: ApplicationCommentCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    application = await _get_or_404(db, application_id)
    return await application_service.add_comment(db, application, data.comment, admin)


@router.get(
    "/{application_id}/history", response_model=list[HistoryOut], dependencies=[Depends(require_any_admin)]
)
async def get_history(application_id: int, db: AsyncSession = Depends(get_db)):
    application = await _get_or_404(db, application_id)
    return application.history
