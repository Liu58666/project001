"""create user_images table

Revision ID: 0009_create_user_images
Revises: 0008_create_user_resumes
Create Date: 2025-12-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0009_create_user_images"
down_revision: Union[str, None] = "0008_create_user_resumes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "user_images" not in inspector.get_table_names():
        op.create_table(
            "user_images",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                comment="关联的用户ID",
            ),
            sa.Column(
                "image_type",
                sa.String(length=50),
                nullable=False,
                comment="图片类型：avatar/certificate/project/portfolio/bio 等",
            ),
            sa.Column(
                "cos_key",
                sa.String(length=500),
                nullable=False,
                comment="腾讯云COS对象键（文件路径）",
            ),
            sa.Column("url", sa.String(length=1000), nullable=False, comment="完整访问URL"),
            sa.Column("original_filename", sa.String(length=255), nullable=False, comment="原始文件名"),
            sa.Column("file_size", sa.Integer(), nullable=False, comment="文件大小（字节）"),
            sa.Column("width", sa.Integer(), nullable=False, comment="图片宽度（像素）"),
            sa.Column("height", sa.Integer(), nullable=False, comment="图片高度（像素）"),
            sa.Column(
                "caption",
                sa.String(length=500),
                nullable=False,
                server_default="",
                comment="图片说明/标题",
            ),
            sa.Column(
                "display_order",
                sa.Integer(),
                nullable=False,
                server_default="0",
                comment="展示顺序（越小越靠前）",
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

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("user_images")}
    if "ix_user_images_user_id" not in existing_indexes:
        op.create_index("ix_user_images_user_id", "user_images", ["user_id"])
    if "ix_user_images_image_type" not in existing_indexes:
        op.create_index("ix_user_images_image_type", "user_images", ["image_type"])
    if "ix_user_images_display_order" not in existing_indexes:
        op.create_index("ix_user_images_display_order", "user_images", ["display_order"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "user_images" not in inspector.get_table_names():
        return

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("user_images")}
    if "ix_user_images_display_order" in existing_indexes:
        op.drop_index("ix_user_images_display_order", table_name="user_images")
    if "ix_user_images_image_type" in existing_indexes:
        op.drop_index("ix_user_images_image_type", table_name="user_images")
    if "ix_user_images_user_id" in existing_indexes:
        op.drop_index("ix_user_images_user_id", table_name="user_images")
    op.drop_table("user_images")


