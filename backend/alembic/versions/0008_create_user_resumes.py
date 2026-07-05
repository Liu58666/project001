"""create user_resumes table

Revision ID: 0008_create_user_resumes
Revises: 0007_add_caption_to_news_images
Create Date: 2025-12-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0008_create_user_resumes"
down_revision: Union[str, None] = "0007_add_caption_to_news_images"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "user_resumes" not in inspector.get_table_names():
        op.create_table(
            "user_resumes",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                comment="关联的用户ID（一对一）",
            ),
            sa.Column("real_name", sa.String(length=100), nullable=False, comment="真实姓名"),
            sa.Column("gender", sa.String(length=10), nullable=True, comment="性别：male/female/other"),
            sa.Column("age", sa.Integer(), nullable=True, comment="年龄"),
            sa.Column("address", sa.String(length=500), nullable=True, comment="地址"),
            sa.Column("bio", sa.JSON(), nullable=True, comment="个人简介段落数组（可含图片占位符）"),
            sa.Column(
                "is_public",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("1"),
                comment="是否公开展示",
            ),
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

    # indexes (idempotent)
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("user_resumes")}
    if "uq_user_resumes_user_id" not in existing_indexes:
        op.create_index("uq_user_resumes_user_id", "user_resumes", ["user_id"], unique=True)
    if "ix_user_resumes_is_public" not in existing_indexes:
        op.create_index("ix_user_resumes_is_public", "user_resumes", ["is_public"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "user_resumes" not in inspector.get_table_names():
        return

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("user_resumes")}
    if "ix_user_resumes_is_public" in existing_indexes:
        op.drop_index("ix_user_resumes_is_public", table_name="user_resumes")
    if "uq_user_resumes_user_id" in existing_indexes:
        op.drop_index("uq_user_resumes_user_id", table_name="user_resumes")
    op.drop_table("user_resumes")


