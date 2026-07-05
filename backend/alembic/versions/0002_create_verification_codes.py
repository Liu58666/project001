"""create verification_codes table

Revision ID: 0002_create_verification_codes
Revises: 0001_create_users
Create Date: 2025-12-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0002_create_verification_codes"
down_revision: Union[str, None] = "0001_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "verification_codes" not in inspector.get_table_names():
        op.create_table(
            "verification_codes",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("phone", sa.String(length=20), nullable=False),
            sa.Column("code", sa.String(length=10), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column(
                "is_used", sa.Boolean(), nullable=False, server_default=sa.text("0")
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
        inspector = inspect(bind)  # refresh after DDL

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("verification_codes")}
    if "ix_verification_codes_phone" not in existing_indexes:
        op.create_index("ix_verification_codes_phone", "verification_codes", ["phone"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "verification_codes" in inspector.get_table_names():
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("verification_codes")}
        if "ix_verification_codes_phone" in existing_indexes:
            op.drop_index("ix_verification_codes_phone", table_name="verification_codes")
        op.drop_table("verification_codes")

