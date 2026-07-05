"""add caption to news_images

Revision ID: 0007_add_caption_to_news_images
Revises: 0006_create_news_images
Create Date: 2025-12-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0007_add_caption_to_news_images"
down_revision: Union[str, None] = "0006_create_news_images"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "news_images" not in inspector.get_table_names():
        return

    # 检查列是否已存在
    columns = [col["name"] for col in inspector.get_columns("news_images")]
    if "caption" not in columns:
        op.add_column(
            "news_images",
            sa.Column(
                "caption",
                sa.String(length=500),
                nullable=False,
                server_default="",
                comment="图片说明",
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "news_images" not in inspector.get_table_names():
        return

    columns = [col["name"] for col in inspector.get_columns("news_images")]
    if "caption" in columns:
        op.drop_column("news_images", "caption")

