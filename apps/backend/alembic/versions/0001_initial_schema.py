"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_user_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_username", sa.String(64), nullable=True),
        sa.Column("first_name", sa.String(128), nullable=True),
        sa.Column("last_name", sa.String(128), nullable=True),
        sa.Column("phone_number", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_telegram_user_id", "users", ["telegram_user_id"], unique=True)

    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.String(32),
            nullable=False,
            server_default="OPERATOR",
        ),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_admins_email", "admins", ["email"], unique=True)

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_number", sa.String(32), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("personal_account", sa.String(32), nullable=False),
        sa.Column("application_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="NEW"),
        sa.Column("priority", sa.String(32), nullable=False, server_default="NORMAL"),
        sa.Column("requested_date", sa.Date(), nullable=True),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("admins.id", ondelete="SET NULL"), nullable=True),
        sa.Column("admin_comment", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_applications_application_number", "applications", ["application_number"], unique=True)
    op.create_index("ix_applications_personal_account", "applications", ["personal_account"])
    op.create_index("ix_applications_status", "applications", ["status"])
    op.create_index("ix_applications_priority", "applications", ["priority"])
    op.create_index("ix_applications_user_id", "applications", ["user_id"])

    op.create_table(
        "application_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_type", sa.String(32), nullable=False),
        sa.Column("telegram_file_id", sa.String(255), nullable=True),
        sa.Column("storage_url", sa.String(512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_application_files_application_id", "application_files", ["application_id"])

    op.create_table(
        "application_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("admin_id", sa.Integer(), sa.ForeignKey("admins.id", ondelete="SET NULL"), nullable=True),
        sa.Column("old_status", sa.String(32), nullable=True),
        sa.Column("new_status", sa.String(32), nullable=False),
        sa.Column("comment", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_application_history_application_id", "application_history", ["application_id"])

    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_name", sa.String(255), nullable=False, server_default="KazGaza"),
        sa.Column("contact_phone", sa.String(32), nullable=False, server_default=""),
        sa.Column("emergency_phone", sa.String(32), nullable=False, server_default=""),
        sa.Column("max_photo_size_mb", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("welcome_text", sa.String(2000), nullable=False, server_default=""),
        sa.Column("status_new_text", sa.String(500), nullable=False, server_default=""),
        sa.Column("status_in_progress_text", sa.String(500), nullable=False, server_default=""),
        sa.Column("status_completed_text", sa.String(500), nullable=False, server_default=""),
        sa.Column("status_rejected_text", sa.String(500), nullable=False, server_default=""),
    )
    op.execute(
        "INSERT INTO system_settings (id, organization_name, contact_phone, emergency_phone, "
        "welcome_text, status_new_text, status_in_progress_text, status_completed_text, status_rejected_text) "
        "VALUES (1, 'KazGaza', '', '', "
        "'Қош келдіңіз! Өтінім қалдыру үшін дербес шотыңызды енгізіңіз.', "
        "'🆕 Өтініміңіз тіркелді.', '🟡 Өтініміңіз өңдеуге алынды.', "
        "'✅ Өтініміңіз орындалды.', '❌ Өтінім қабылданбады.')"
    )


def downgrade() -> None:
    op.drop_table("system_settings")
    op.drop_table("application_history")
    op.drop_table("application_files")
    op.drop_table("applications")
    op.drop_table("admins")
    op.drop_table("users")
