"""add role to user_resumes (sync with users.role)

Revision ID: 0011_resume_role
Revises: 0010_resume_fields
Create Date: 2025-12-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0011_resume_role"
down_revision: Union[str, None] = "0010_resume_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "user_resumes" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("user_resumes")}
    if "role" not in columns:
        op.add_column(
            "user_resumes",
            sa.Column(
                "role",
                sa.SmallInteger(),
                nullable=False,
                server_default="0",
                comment="冗余字段：与 users.role 保持一致",
            ),
        )

    # backfill from users.role (best-effort)
    try:
        op.execute(
            sa.text(
                "UPDATE user_resumes ur "
                "JOIN users u ON ur.user_id = u.id "
                "SET ur.role = u.role"
            )
        )
    except Exception:
        # If DB dialect doesn't support join update or permissions limited, skip.
        pass


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "user_resumes" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("user_resumes")}
    if "role" in columns:
        op.drop_column("user_resumes", "role")


