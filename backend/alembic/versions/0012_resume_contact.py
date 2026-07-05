"""add phone/email to user_resumes (sync with users profile)

Revision ID: 0012_resume_contact
Revises: 0011_resume_role
Create Date: 2025-12-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0012_resume_contact"
down_revision: Union[str, None] = "0011_resume_role"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "user_resumes" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("user_resumes")}
    if "phone" not in columns:
        op.add_column(
            "user_resumes",
            sa.Column("phone", sa.String(length=20), nullable=True, comment="联系电话（与 users.phone 同步）"),
        )
    if "email" not in columns:
        op.add_column(
            "user_resumes",
            sa.Column("email", sa.String(length=255), nullable=True, comment="邮箱（与 users.email 同步）"),
        )

    # backfill from users (best-effort)
    try:
        op.execute(
            sa.text(
                "UPDATE user_resumes ur "
                "JOIN users u ON ur.user_id = u.id "
                "SET ur.phone = u.phone, ur.email = u.email"
            )
        )
    except Exception:
        pass


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "user_resumes" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("user_resumes")}
    if "email" in columns:
        op.drop_column("user_resumes", "email")
    if "phone" in columns:
        op.drop_column("user_resumes", "phone")


