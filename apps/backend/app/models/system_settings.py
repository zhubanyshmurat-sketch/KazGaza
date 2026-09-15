from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin


class SystemSettings(Base):
    """Single-row key/value style config table for org-wide settings.

    Modeled as one row (id=1) with typed columns rather than an EAV table
    since the set of settings is small and fixed.
    """

    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    organization_name: Mapped[str] = mapped_column(String(255), default="KazGaza")
    contact_phone: Mapped[str] = mapped_column(String(32), default="")
    emergency_phone: Mapped[str] = mapped_column(String(32), default="")
    max_photo_size_mb: Mapped[int] = mapped_column(default=10)
    welcome_text: Mapped[str] = mapped_column(
        String(2000),
        default="Қош келдіңіз! Өтінім қалдыру үшін дербес шотыңызды енгізіңіз.",
    )
    status_new_text: Mapped[str] = mapped_column(String(500), default="🆕 Өтініміңіз тіркелді.")
    status_in_progress_text: Mapped[str] = mapped_column(
        String(500), default="🟡 Өтініміңіз өңдеуге алынды."
    )
    status_completed_text: Mapped[str] = mapped_column(String(500), default="✅ Өтініміңіз орындалды.")
    status_rejected_text: Mapped[str] = mapped_column(String(500), default="❌ Өтінім қабылданбады.")
