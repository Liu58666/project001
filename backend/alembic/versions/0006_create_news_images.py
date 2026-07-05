"""create news_images table

Revision ID: 0006_create_news_images
Revises: 0005_create_refresh_tokens
Create Date: 2025-12-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0006_create_news_images"
down_revision: Union[str, None] = "0005_create_refresh_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "news_images" not in inspector.get_table_names():
        op.create_table(
            "news_images",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "news_id",
                sa.Integer(),
                sa.ForeignKey("news.id", ondelete="CASCADE"),
                nullable=True,
                comment="关联的新闻ID，可为空（未关联时）",
            ),
            sa.Column(
                "position",
                sa.String(length=50),
                nullable=False,
                comment="图片位置：cover(封面), content(内容), thumbnail(缩略图), banner(横幅)等",
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
                "uploaded_by",
                sa.Integer(),
                sa.ForeignKey("users.id"),
                nullable=False,
                comment="上传用户ID",
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

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("news_images")}
    if "ix_news_images_news_id" not in existing_indexes:
        op.create_index("ix_news_images_news_id", "news_images", ["news_id"])
    if "ix_news_images_position" not in existing_indexes:
        op.create_index("ix_news_images_position", "news_images", ["position"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "news_images" not in inspector.get_table_names():
        return

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("news_images")}
    if "ix_news_images_position" in existing_indexes:
        op.drop_index("ix_news_images_position", table_name="news_images")
    if "ix_news_images_news_id" in existing_indexes:
        op.drop_index("ix_news_images_news_id", table_name="news_images")
    op.drop_table("news_images")


