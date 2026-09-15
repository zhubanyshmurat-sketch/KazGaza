from datetime import date, datetime
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from kazgaza_shared import ApplicationPriority, ApplicationStatus, ApplicationType

DETAIL_OPTIONS = (
    selectinload(Application.user),
    selectinload(Application.assigned_admin),
    selectinload(Application.files),
    selectinload(Application.history),
)


async def get_by_id(db: AsyncSession, application_id: int, with_relations: bool = True) -> Application | None:
    stmt = select(Application).where(Application.id == application_id)
    if with_relations:
        stmt = stmt.options(*DETAIL_OPTIONS)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_number(db: AsyncSession, application_number: str) -> Application | None:
    stmt = select(Application).where(Application.application_number == application_number).options(*DETAIL_OPTIONS)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def next_sequence_for_today(db: AsyncSession, today: date) -> int:
    prefix = f"REQ-{today.strftime('%Y%m%d')}-"
    result = await db.execute(
        select(func.count()).select_from(Application).where(Application.application_number.like(f"{prefix}%"))
    )
    return (result.scalar_one() or 0) + 1


async def list_for_user(db: AsyncSession, user_id: int, limit: int = 10) -> Sequence[Application]:
    result = await db.execute(
        select(Application)
        .where(Application.user_id == user_id)
        .order_by(Application.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def search(
    db: AsyncSession,
    *,
    application_number: str | None = None,
    personal_account: str | None = None,
    application_type: ApplicationType | None = None,
    status: ApplicationStatus | None = None,
    priority: ApplicationPriority | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    query: str | None = None,
    assigned_to: int | None = None,
    sort: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Application], int]:
    stmt = select(Application).options(*DETAIL_OPTIONS)
    count_stmt = select(func.count()).select_from(Application)

    conditions = []
    if application_number:
        conditions.append(Application.application_number.ilike(f"%{application_number}%"))
    if personal_account:
        conditions.append(Application.personal_account.ilike(f"%{personal_account}%"))
    if application_type:
        conditions.append(Application.application_type == application_type)
    if status:
        conditions.append(Application.status == status)
    if priority:
        conditions.append(Application.priority == priority)
    if date_from:
        conditions.append(Application.created_at >= date_from)
    if date_to:
        conditions.append(Application.created_at <= date_to)
    if assigned_to:
        conditions.append(Application.assigned_to == assigned_to)
    if query:
        conditions.append(
            (Application.application_number.ilike(f"%{query}%"))
            | (Application.personal_account.ilike(f"%{query}%"))
        )

    for cond in conditions:
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    total = (await db.execute(count_stmt)).scalar_one()

    order_col = Application.created_at.asc() if sort == "asc" else Application.created_at.desc()
    stmt = stmt.order_by(order_col).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(stmt)).scalars().all()
    return list(items), total
