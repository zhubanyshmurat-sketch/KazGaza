from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.auth.rbac import require_any_admin
from app.schemas.dashboard import DashboardStats, ReportStats
from app.services.report_service import build_report
from app.services.stats_service import get_dashboard_stats
from kazgaza_shared import ApplicationStatus, ApplicationType

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(require_any_admin)])


@router.get("/stats", response_model=DashboardStats)
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    return await get_dashboard_stats(db)


@router.get("/report", response_model=ReportStats)
async def dashboard_report(
    db: AsyncSession = Depends(get_db),
    application_type: ApplicationType | None = None,
    status: ApplicationStatus | None = None,
    assigned_to: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    return await build_report(
        db,
        application_type=application_type,
        status=status,
        assigned_to=assigned_to,
        date_from=date_from,
        date_to=date_to,
    )
