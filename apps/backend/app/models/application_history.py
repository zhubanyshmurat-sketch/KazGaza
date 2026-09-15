from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from kazgaza_shared import ApplicationStatus


class ApplicationHistory(Base):
    __tablename__ = "application_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    admin_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("admins.id", ondelete="SET NULL"), nullable=True
    )
    old_status: Mapped[Optional[ApplicationStatus]] = mapped_column(
        Enum(ApplicationStatus, name="application_status", native_enum=False, length=32), nullable=True
    )
    new_status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", native_enum=False, length=32), nullable=False
    )
    comment: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["Application"] = relationship(back_populates="history")
    admin: Mapped[Optional["Admin"]] = relationship()
