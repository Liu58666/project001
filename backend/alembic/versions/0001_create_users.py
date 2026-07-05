"""create users table

Revision ID: 0001_create_users
Revises:
Create Date: 2025-12-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0001_create_users"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "users" not in inspector.get_table_names():
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("username", sa.String(length=50), nullable=False),
            sa.Column("phone", sa.String(length=20), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("role", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
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
            sa.UniqueConstraint("username", name="uq_users_username"),
            sa.UniqueConstraint("phone", name="uq_users_phone"),
        )
        inspector = inspect(bind)  # refresh after DDL

    # Ensure indexes exist (idempotent)
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("users")}
    if "ix_users_username" not in existing_indexes:
        op.create_index("ix_users_username", "users", ["username"], unique=True)
    if "ix_users_phone" not in existing_indexes:
        op.create_index("ix_users_phone", "users", ["phone"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "users" in inspector.get_table_names():
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("users")}
        if "ix_users_username" in existing_indexes:
            op.drop_index("ix_users_username", table_name="users")
        if "ix_users_phone" in existing_indexes:
            op.drop_index("ix_users_phone", table_name="users")
        op.drop_table("users")



