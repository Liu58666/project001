"""add email/birthday/photo to users

Revision ID: 0003_add_user_profile_fields
Revises: 0002_create_verification_codes
Create Date: 2025-12-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0003_add_user_profile_fields"
down_revision: Union[str, None] = "0002_create_verification_codes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "users" not in inspector.get_table_names():
        # Repair-path: if migration history says users should exist but it doesn't, create it here
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("username", sa.String(length=50), nullable=False),
            sa.Column("phone", sa.String(length=20), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("role", sa.SmallInteger(), nullable=False, server_default=sa.text("0")),
            sa.Column("email", sa.String(length=255), nullable=True),
            sa.Column("birthday", sa.Date(), nullable=True),
            sa.Column("photo", sa.String(length=255), nullable=False, server_default=sa.text("''")),
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
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("users")}
        if "ix_users_username" not in existing_indexes:
            op.create_index("ix_users_username", "users", ["username"], unique=True)
        if "ix_users_phone" not in existing_indexes:
            op.create_index("ix_users_phone", "users", ["phone"], unique=True)
        return

    existing_columns = {col["name"] for col in inspector.get_columns("users")}
    if "email" not in existing_columns:
        op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    if "birthday" not in existing_columns:
        op.add_column("users", sa.Column("birthday", sa.Date(), nullable=True))
    if "photo" not in existing_columns:
        op.add_column(
            "users",
            sa.Column(
                "photo", sa.String(length=255), nullable=False, server_default=sa.text("''")
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("users")}
    if "photo" in existing_columns:
        op.drop_column("users", "photo")
    if "birthday" in existing_columns:
        op.drop_column("users", "birthday")
    if "email" in existing_columns:
        op.drop_column("users", "email")


