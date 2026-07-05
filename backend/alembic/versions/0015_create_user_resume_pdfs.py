"""create user_resume_pdfs table

Revision ID: 0015_resume_pdfs
Revises: 0014_tasks_submit
Create Date: 2026-01-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0015_resume_pdfs"
down_revision: Union[str, None] = "0014_tasks_submit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "user_resume_pdfs" not in inspector.get_table_names():
        op.create_table(
            "user_resume_pdfs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                comment="关联的用户ID（一对一：同一用户仅保留最新一份PDF简历）",
            ),
            sa.Column("cos_key", sa.String(length=500), nullable=False, comment="腾讯云COS对象键（文件路径）"),
            sa.Column("url", sa.String(length=1000), nullable=False, comment="完整访问URL（公开直链）"),
            sa.Column("original_filename", sa.String(length=255), nullable=False, comment="原始文件名"),
            sa.Column("file_size", sa.Integer(), nullable=False, comment="文件大小（字节）"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
        inspector = inspect(bind)  # refresh after DDL

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("user_resume_pdfs")}
    if "uq_user_resume_pdfs_user_id" not in existing_indexes:
        op.create_index(
            "uq_user_resume_pdfs_user_id",
            "user_resume_pdfs",
            ["user_id"],
            unique=True,
        )
    if "ix_user_resume_pdfs_updated_at" not in existing_indexes:
        op.create_index("ix_user_resume_pdfs_updated_at", "user_resume_pdfs", ["updated_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "user_resume_pdfs" not in inspector.get_table_names():
        return
    op.drop_table("user_resume_pdfs")


