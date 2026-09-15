from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from kazgaza_shared import FileType


class ApplicationFile(Base):
    __tablename__ = "application_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_type: Mapped[FileType] = mapped_column(
        Enum(FileType, name="application_file_type", native_enum=False, length=32), nullable=False
    )
    telegram_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    storage_url: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["Application"] = relationship(back_populates="files")
