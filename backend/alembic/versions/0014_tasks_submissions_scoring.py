"""tasks + task recipients + submissions + submission images

Revision ID: 0014_tasks_submit
Revises: 0013_app_forms_msgs
Create Date: 2025-12-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0014_tasks_submit"
down_revision: Union[str, None] = "0013_app_forms_msgs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _index_names(inspector, table: str) -> set[str]:
    return {idx["name"] for idx in inspector.get_indexes(table)}


def _table_names(inspector) -> set[str]:
    return set(inspector.get_table_names())


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = _table_names(inspector)

    #
    # tasks
    #
    if "tasks" not in tables:
        op.create_table(
            "tasks",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("title", sa.String(length=200), nullable=False, comment="任务标题"),
            sa.Column("content", sa.String(length=5000), nullable=False, comment="任务内容（纯文本）"),
            sa.Column(
                "created_by",
                sa.Integer(),
                sa.ForeignKey("users.id"),
                nullable=False,
                comment="创建人用户ID（role in {3,4}）",
            ),
            sa.Column("published_at", sa.DateTime(timezone=True), nullable=True, comment="发布时间（可为空）"),
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
        inspector = inspect(bind)
        tables = _table_names(inspector)

    if "tasks" in tables:
        idx = _index_names(inspector, "tasks")
        if "ix_tasks_created_by" not in idx:
            op.create_index("ix_tasks_created_by", "tasks", ["created_by"])
        if "ix_tasks_published_at" not in idx:
            op.create_index("ix_tasks_published_at", "tasks", ["published_at"])
        if "ix_tasks_created_at" not in idx:
            op.create_index("ix_tasks_created_at", "tasks", ["created_at"])

    #
    # task_recipients
    #
    inspector = inspect(bind)
    tables = _table_names(inspector)
    if "task_recipients" not in tables:
        op.create_table(
            "task_recipients",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "task_id",
                sa.Integer(),
                sa.ForeignKey("tasks.id", ondelete="CASCADE"),
                nullable=False,
                comment="任务ID",
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                comment="接收者用户ID（发布时快照）",
            ),
            sa.Column(
                "assigned_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
                comment="指派时间",
            ),
        )
        inspector = inspect(bind)
        tables = _table_names(inspector)

    if "task_recipients" in tables:
        idx = _index_names(inspector, "task_recipients")
        if "uq_task_recipients_task_id_user_id" not in idx:
            op.create_index(
                "uq_task_recipients_task_id_user_id",
                "task_recipients",
                ["task_id", "user_id"],
                unique=True,
            )
        if "ix_task_recipients_task_id" not in idx:
            op.create_index("ix_task_recipients_task_id", "task_recipients", ["task_id"])
        if "ix_task_recipients_user_id" not in idx:
            op.create_index("ix_task_recipients_user_id", "task_recipients", ["user_id"])

    #
    # task_submissions
    #
    inspector = inspect(bind)
    tables = _table_names(inspector)
    if "task_submissions" not in tables:
        op.create_table(
            "task_submissions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "task_id",
                sa.Integer(),
                sa.ForeignKey("tasks.id", ondelete="CASCADE"),
                nullable=False,
                comment="任务ID",
            ),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                comment="提交者用户ID",
            ),
            sa.Column("text_content", sa.String(length=5000), nullable=True, comment="提交内容（纯文本）"),
            sa.Column("suggestion", sa.String(length=2000), nullable=True, comment="建议（纯文本）"),
            sa.Column("score", sa.SmallInteger(), nullable=True, comment="评分（0-100，role>=3）"),
            sa.Column("scored_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True, comment="评分人用户ID（role>=3）"),
            sa.Column("scored_at", sa.DateTime(timezone=True), nullable=True, comment="评分时间"),
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
        inspector = inspect(bind)
        tables = _table_names(inspector)

    if "task_submissions" in tables:
        idx = _index_names(inspector, "task_submissions")
        if "uq_task_submissions_task_id_user_id" not in idx:
            op.create_index(
                "uq_task_submissions_task_id_user_id",
                "task_submissions",
                ["task_id", "user_id"],
                unique=True,
            )
        if "ix_task_submissions_task_id" not in idx:
            op.create_index("ix_task_submissions_task_id", "task_submissions", ["task_id"])
        if "ix_task_submissions_user_id" not in idx:
            op.create_index("ix_task_submissions_user_id", "task_submissions", ["user_id"])
        if "ix_task_submissions_updated_at" not in idx:
            op.create_index("ix_task_submissions_updated_at", "task_submissions", ["updated_at"])

    #
    # task_submission_images
    #
    inspector = inspect(bind)
    tables = _table_names(inspector)
    if "task_submission_images" not in tables:
        op.create_table(
            "task_submission_images",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "submission_id",
                sa.Integer(),
                sa.ForeignKey("task_submissions.id", ondelete="CASCADE"),
                nullable=False,
                comment="关联的提交ID",
            ),
            sa.Column("cos_key", sa.String(length=500), nullable=False, comment="腾讯云COS对象键（文件路径）"),
            sa.Column("url", sa.String(length=1000), nullable=False, comment="完整访问URL"),
            sa.Column("original_filename", sa.String(length=255), nullable=False, comment="原始文件名"),
            sa.Column("file_size", sa.Integer(), nullable=False, comment="文件大小（字节）"),
            sa.Column("width", sa.Integer(), nullable=False, comment="图片宽度（像素）"),
            sa.Column("height", sa.Integer(), nullable=False, comment="图片高度（像素）"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
        )
        inspector = inspect(bind)

    inspector = inspect(bind)
    tables = _table_names(inspector)
    if "task_submission_images" in tables:
        idx = _index_names(inspector, "task_submission_images")
        if "ix_task_submission_images_submission_id" not in idx:
            op.create_index(
                "ix_task_submission_images_submission_id",
                "task_submission_images",
                ["submission_id"],
            )
        if "ix_task_submission_images_created_at" not in idx:
            op.create_index(
                "ix_task_submission_images_created_at",
                "task_submission_images",
                ["created_at"],
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = _table_names(inspector)

    if "task_submission_images" in tables:
        op.drop_table("task_submission_images")

    inspector = inspect(bind)
    tables = _table_names(inspector)
    if "task_submissions" in tables:
        op.drop_table("task_submissions")

    inspector = inspect(bind)
    tables = _table_names(inspector)
    if "task_recipients" in tables:
        op.drop_table("task_recipients")

    inspector = inspect(bind)
    tables = _table_names(inspector)
    if "tasks" in tables:
        op.drop_table("tasks")


