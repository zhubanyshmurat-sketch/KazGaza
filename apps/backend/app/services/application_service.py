from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import Admin
from app.models.application import Application
from app.models.application_file import ApplicationFile
from app.models.application_history import ApplicationHistory
from app.notifications.telegram_client import send_telegram_message
from app.notifications.ws_manager import manager
from app.repositories import application_repo, user_repo
from app.schemas.application import ApplicationCreateBot
from app.services import file_service
from app.services.account_service import verify_personal_account
from app.services.settings_service import get_settings_row
from kazgaza_shared import ApplicationPriority, ApplicationStatus, ApplicationType

STATUS_TEXT_FIELD = {
    ApplicationStatus.NEW: "status_new_text",
    ApplicationStatus.IN_PROGRESS: "status_in_progress_text",
    ApplicationStatus.COMPLETED: "status_completed_text",
    ApplicationStatus.REJECTED: "status_rejected_text",
}


async def _generate_application_number(db: AsyncSession, today: date) -> str:
    seq = await application_repo.next_sequence_for_today(db, today)
    return f"REQ-{today.strftime('%Y%m%d')}-{seq:05d}"


def _priority_for_type(application_type: ApplicationType) -> ApplicationPriority:
    return ApplicationPriority.CRITICAL if application_type == ApplicationType.GAS_LEAK else ApplicationPriority.NORMAL


async def create_application_from_bot(db: AsyncSession, payload: ApplicationCreateBot) -> Application:
    ok, error = verify_personal_account(payload.personal_account)
    if not ok:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, error)

    user = await user_repo.get_by_telegram_id(db, payload.telegram_user_id)
    if not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Пайдаланушы тіркелмеген.")

    required_types = file_service.REQUIRED_PHOTOS[payload.application_type.value]
    provided_types = {p.file_type for p in payload.photos}
    if not required_types.issubset(provided_types):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Міндетті фотосуреттер жіберілмеген.")

    if payload.application_type == ApplicationType.MPI_REMOVAL and not payload.requested_date:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "МПИ-ге шешу күні көрсетілмеген.")

    if payload.application_type in (ApplicationType.METER_NOT_WORKING, ApplicationType.GAS_LEAK):
        if payload.latitude is None or payload.longitude is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Геолокация көрсетілмеген.")

    today = datetime.now(timezone.utc).date()
    application_number = await _generate_application_number(db, today)

    application = Application(
        application_number=application_number,
        user_id=user.id,
        personal_account=payload.personal_account,
        application_type=payload.application_type,
        status=ApplicationStatus.NEW,
        priority=_priority_for_type(payload.application_type),
        requested_date=payload.requested_date,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(application)
    await db.flush()

    for photo in payload.photos:
        storage_url = await file_service.download_validate_store(photo.telegram_file_id, application_number)
        db.add(
            ApplicationFile(
                application_id=application.id,
                file_type=photo.file_type,
                telegram_file_id=photo.telegram_file_id,
                storage_url=storage_url,
            )
        )

    db.add(
        ApplicationHistory(
            application_id=application.id,
            admin_id=None,
            old_status=None,
            new_status=ApplicationStatus.NEW,
            comment="Өтінім Telegram bot арқылы құрылды.",
        )
    )
    await db.commit()
    application = await application_repo.get_by_id(db, application.id)

    await manager.broadcast(
        "application_created",
        {
            "id": application.id,
            "application_number": application.application_number,
            "application_type": application.application_type.value,
            "priority": application.priority.value,
            "status": application.status.value,
        },
    )
    return application


async def change_status(
    db: AsyncSession,
    application: Application,
    new_status: ApplicationStatus,
    comment: str | None,
    admin: Admin,
) -> Application:
    old_status = application.status
    application.status = new_status
    if comment:
        application.admin_comment = comment

    db.add(
        ApplicationHistory(
            application_id=application.id,
            admin_id=admin.id,
            old_status=old_status,
            new_status=new_status,
            comment=comment,
        )
    )
    await db.commit()
    application = await application_repo.get_by_id(db, application.id)

    settings_row = await get_settings_row(db)
    base_text = getattr(settings_row, STATUS_TEXT_FIELD[new_status])
    text = f"{base_text}\n\n№ {application.application_number}"
    if new_status == ApplicationStatus.REJECTED and comment:
        text += f"\n\nСебебі: {comment}"
    elif comment and new_status == ApplicationStatus.COMPLETED:
        text += f"\n\n{comment}"
    await send_telegram_message(application.user.telegram_user_id, text)

    await manager.broadcast(
        "application_status_changed",
        {
            "id": application.id,
            "application_number": application.application_number,
            "status": application.status.value,
            "priority": application.priority.value,
        },
    )
    return application


async def assign_application(
    db: AsyncSession, application: Application, assigned_to: int | None, admin: Admin
) -> Application:
    application.assigned_to = assigned_to
    db.add(
        ApplicationHistory(
            application_id=application.id,
            admin_id=admin.id,
            old_status=application.status,
            new_status=application.status,
            comment="Тағайындау өзгертілді.",
        )
    )
    await db.commit()
    application = await application_repo.get_by_id(db, application.id)
    await manager.broadcast(
        "application_assigned",
        {"id": application.id, "application_number": application.application_number, "assigned_to": assigned_to},
    )
    return application


async def add_comment(db: AsyncSession, application: Application, comment: str, admin: Admin) -> Application:
    db.add(
        ApplicationHistory(
            application_id=application.id,
            admin_id=admin.id,
            old_status=application.status,
            new_status=application.status,
            comment=comment,
        )
    )
    await db.commit()
    return await application_repo.get_by_id(db, application.id)
