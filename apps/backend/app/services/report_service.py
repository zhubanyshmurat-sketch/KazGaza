from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import application_repo
from app.schemas.dashboard import ReportStats
from kazgaza_shared import ApplicationPriority, ApplicationStatus, ApplicationType


async def build_report(
    db: AsyncSession,
    *,
    application_type: ApplicationType | None,
    status: ApplicationStatus | None,
    assigned_to: int | None,
    date_from: datetime | None,
    date_to: datetime | None,
) -> ReportStats:
    items, total = await application_repo.search(
        db,
        application_type=application_type,
        status=status,
        assigned_to=assigned_to,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=100_000,
    )

    new = sum(1 for a in items if a.status == ApplicationStatus.NEW)
    in_progress = sum(1 for a in items if a.status == ApplicationStatus.IN_PROGRESS)
    completed = [a for a in items if a.status == ApplicationStatus.COMPLETED]
    rejected = sum(1 for a in items if a.status == ApplicationStatus.REJECTED)
    critical = sum(1 for a in items if a.priority == ApplicationPriority.CRITICAL)

    if completed:
        # updated_at reflects the most recent status change, which for a
        # COMPLETED application is the moment it was closed out.
        durations_hours = [(a.updated_at - a.created_at).total_seconds() / 3600 for a in completed]
        avg_hours = round(sum(durations_hours) / len(durations_hours), 1)
    else:
        avg_hours = None

    return ReportStats(
        total=total,
        new=new,
        in_progress=in_progress,
        completed=len(completed),
        rejected=rejected,
        critical=critical,
        avg_processing_hours=avg_hours,
    )
