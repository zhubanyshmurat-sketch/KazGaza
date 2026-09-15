from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.schemas.dashboard import DashboardStats
from kazgaza_shared import ApplicationPriority, ApplicationStatus


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    total = (await db.execute(select(func.count()).select_from(Application))).scalar_one()

    async def count_status(s: ApplicationStatus) -> int:
        result = await db.execute(
            select(func.count()).select_from(Application).where(Application.status == s)
        )
        return result.scalar_one()

    new = await count_status(ApplicationStatus.NEW)
    in_progress = await count_status(ApplicationStatus.IN_PROGRESS)
    completed = await count_status(ApplicationStatus.COMPLETED)
    rejected = await count_status(ApplicationStatus.REJECTED)

    critical_result = await db.execute(
        select(func.count())
        .select_from(Application)
        .where(Application.priority == ApplicationPriority.CRITICAL, Application.status != ApplicationStatus.COMPLETED)
    )
    critical = critical_result.scalar_one()

    by_type_result = await db.execute(
        select(Application.application_type, func.count()).group_by(Application.application_type)
    )
    by_type = {row[0].value: row[1] for row in by_type_result.all()}

    since = datetime.now(timezone.utc) - timedelta(days=13)
    by_day_result = await db.execute(
        select(func.date(Application.created_at), func.count())
        .where(Application.created_at >= since)
        .group_by(func.date(Application.created_at))
        .order_by(func.date(Application.created_at))
    )
    by_day = [{"date": str(row[0]), "count": row[1]} for row in by_day_result.all()]

    return DashboardStats(
        total=total,
        new=new,
        in_progress=in_progress,
        completed=completed,
        rejected=rejected,
        critical=critical,
        by_type=by_type,
        by_day=by_day,
    )
