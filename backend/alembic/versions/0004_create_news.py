"""create news table

Revision ID: 0004_create_news
Revises: 0003_add_user_profile_fields
Create Date: 2025-12-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0004_create_news"
down_revision: Union[str, None] = "0003_add_user_profile_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "news" not in inspector.get_table_names():
        op.create_table(
            "news",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("slug", sa.String(length=255), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=False, server_default=sa.text("'News'")),
            sa.Column("published_at", sa.Date(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("subtitle", sa.String(length=500), nullable=False, server_default=sa.text("''")),
            sa.Column("author", sa.String(length=100), nullable=False, server_default=sa.text("'Company'")),
            sa.Column("content", sa.JSON(), nullable=False),
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
            sa.UniqueConstraint("slug", name="uq_news_slug"),
        )
        inspector = inspect(bind)  # refresh after DDL

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("news")}
    if "ix_news_slug" not in existing_indexes:
        op.create_index("ix_news_slug", "news", ["slug"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "news" not in inspector.get_table_names():
        return

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("news")}
    if "ix_news_slug" in existing_indexes:
        op.drop_index("ix_news_slug", table_name="news")
    op.drop_table("news")


