from datetime import date
from typing import List, Optional

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin
from kazgaza_shared import ApplicationPriority, ApplicationStatus, ApplicationType


class Application(TimestampMixin, Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    personal_account: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    application_type: Mapped[ApplicationType] = mapped_column(
        Enum(ApplicationType, name="application_type", native_enum=False, length=32), nullable=False
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", native_enum=False, length=32),
        default=ApplicationStatus.NEW,
        nullable=False,
        index=True,
    )
    priority: Mapped[ApplicationPriority] = mapped_column(
        Enum(ApplicationPriority, name="application_priority", native_enum=False, length=32),
        default=ApplicationPriority.NORMAL,
        nullable=False,
        index=True,
    )
    requested_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    assigned_to: Mapped[Optional[int]] = mapped_column(
        ForeignKey("admins.id", ondelete="SET NULL"), nullable=True
    )
    admin_comment: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    user: Mapped["User"] = relationship(back_populates="applications")
    assigned_admin: Mapped[Optional["Admin"]] = relationship(
        back_populates="assigned_applications", foreign_keys=[assigned_to]
    )
    files: Mapped[List["ApplicationFile"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    history: Mapped[List["ApplicationHistory"]] = relationship(
        back_populates="application", cascade="all, delete-orphan", order_by="ApplicationHistory.created_at"
    )
