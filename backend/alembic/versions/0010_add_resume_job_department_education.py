"""add job_title/department/education to user_resumes

Revision ID: 0010_resume_fields
Revises: 0009_create_user_images
Create Date: 2025-12-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0010_resume_fields"
down_revision: Union[str, None] = "0009_create_user_images"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "user_resumes" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("user_resumes")}
    if "job_title" not in columns:
        op.add_column(
            "user_resumes",
            sa.Column("job_title", sa.String(length=100), nullable=True, comment="职位"),
        )
    if "department" not in columns:
        op.add_column(
            "user_resumes",
            sa.Column("department", sa.String(length=100), nullable=True, comment="部门"),
        )
    if "education" not in columns:
        op.add_column(
            "user_resumes",
            sa.Column("education", sa.String(length=500), nullable=True, comment="教育背景/学历"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "user_resumes" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("user_resumes")}
    if "education" in columns:
        op.drop_column("user_resumes", "education")
    if "department" in columns:
        op.drop_column("user_resumes", "department")
    if "job_title" in columns:
        op.drop_column("user_resumes", "job_title")


