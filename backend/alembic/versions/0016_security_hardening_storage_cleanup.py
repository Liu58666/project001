"""security hardening and storage cleanup jobs

Revision ID: 0016_security_cleanup
Revises: 0015_resume_pdfs
Create Date: 2026-07-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "0016_security_cleanup"
down_revision: Union[str, None] = "0015_resume_pdfs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    return {idx["name"] for idx in inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "verification_codes" in tables:
        cols = _columns("verification_codes")
        if "code_hash" not in cols:
            op.add_column("verification_codes", sa.Column("code_hash", sa.String(length=64), nullable=True))
        op.execute("UPDATE verification_codes SET is_used = 1 WHERE is_used = 0")

    if "news_images" in tables:
        cols = _columns("news_images")
        if "display_order" not in cols:
            op.add_column(
                "news_images",
                sa.Column("display_order", sa.Integer(), server_default="0", nullable=False, comment="新闻内展示顺序"),
            )
        indexes = _indexes("news_images")
        if "ix_news_images_display_order" not in indexes:
            op.create_index("ix_news_images_display_order", "news_images", ["display_order"])

    if "storage_cleanup_jobs" not in tables:
        op.create_table(
            "storage_cleanup_jobs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("cos_key", sa.String(length=500), nullable=False),
            sa.Column("source_table", sa.String(length=100), nullable=False),
            sa.Column("source_id", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
            sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
            sa.Column("last_error", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index(
            "ix_storage_cleanup_jobs_status_created",
            "storage_cleanup_jobs",
            ["status", "created_at"],
        )
        op.create_index("ix_storage_cleanup_jobs_cos_key", "storage_cleanup_jobs", ["cos_key"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "storage_cleanup_jobs" in tables:
        op.drop_table("storage_cleanup_jobs")

    if "news_images" in tables:
        indexes = _indexes("news_images")
        if "ix_news_images_display_order" in indexes:
            op.drop_index("ix_news_images_display_order", table_name="news_images")
        cols = _columns("news_images")
        if "display_order" in cols:
            op.drop_column("news_images", "display_order")

    if "verification_codes" in tables:
        cols = _columns("verification_codes")
        if "code_hash" in cols:
            op.drop_column("verification_codes", "code_hash")
