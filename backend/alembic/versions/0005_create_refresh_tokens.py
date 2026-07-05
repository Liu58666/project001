"""create refresh_tokens table

Revision ID: 0005_create_refresh_tokens
Revises: 0004_create_news
Create Date: 2025-12-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0005_create_refresh_tokens"
down_revision: Union[str, None] = "0004_create_news"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "refresh_tokens" not in inspector.get_table_names():
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("replaced_by_id", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_refresh_tokens_user_id"),
            sa.ForeignKeyConstraint(
                ["replaced_by_id"],
                ["refresh_tokens.id"],
                name="fk_refresh_tokens_replaced_by_id",
            ),
        )
        inspector = inspect(bind)  # refresh after DDL

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("refresh_tokens")}

    if "uq_refresh_tokens_token_hash" not in existing_indexes:
        op.create_index(
            "uq_refresh_tokens_token_hash",
            "refresh_tokens",
            ["token_hash"],
            unique=True,
        )
    if "ix_refresh_tokens_user_id" not in existing_indexes:
        op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    if "ix_refresh_tokens_expires_at" not in existing_indexes:
        op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "refresh_tokens" not in inspector.get_table_names():
        return

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("refresh_tokens")}
    if "uq_refresh_tokens_token_hash" in existing_indexes:
        op.drop_index("uq_refresh_tokens_token_hash", table_name="refresh_tokens")
    if "ix_refresh_tokens_user_id" in existing_indexes:
        op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    if "ix_refresh_tokens_expires_at" in existing_indexes:
        op.drop_index("ix_refresh_tokens_expires_at", table_name="refresh_tokens")

    op.drop_table("refresh_tokens")

