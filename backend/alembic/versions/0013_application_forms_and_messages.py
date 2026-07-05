"""application forms + system messages (with broadcast revoke support)

Revision ID: 0013_app_forms_msgs
Revises: 0012_resume_contact
Create Date: 2025-12-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "0013_app_forms_msgs"
down_revision: Union[str, None] = "0012_resume_contact"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _index_names(inspector, table: str) -> set[str]:
    return {idx["name"] for idx in inspector.get_indexes(table)}


def _column_names(inspector, table: str) -> set[str]:
    return {col["name"] for col in inspector.get_columns(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    #
    # user_application_forms
    #
    if "user_application_forms" not in tables:
        op.create_table(
            "user_application_forms",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                comment="关联的用户ID（一对一：同一用户只能提交一次）",
            ),
            sa.Column("name", sa.String(length=100), nullable=True, comment="姓名"),
            sa.Column("grade", sa.String(length=50), nullable=True, comment="年级"),
            sa.Column("age", sa.Integer(), nullable=True, comment="年龄"),
            sa.Column("major", sa.String(length=100), nullable=True, comment="专业"),
            sa.Column("school", sa.String(length=255), nullable=True, comment="学校"),
            sa.Column("preference", sa.String(length=20), nullable=True, comment="更倾向于：科研/开发/均可"),
            sa.Column("experience", sa.String(length=5000), nullable=True, comment="我的经历（纯文本）"),
            sa.Column("message", sa.String(length=2000), nullable=True, comment="有没有什么想对我们说？"),
            sa.Column("participated_before", sa.Boolean(), nullable=True, comment="之前是否有参与过我们的课程？"),
            sa.Column("status", sa.SmallInteger(), nullable=False, server_default=sa.text("0"), comment="审核状态"),
            sa.Column(
                "reviewed_by",
                sa.Integer(),
                sa.ForeignKey("users.id"),
                nullable=True,
                comment="审核人用户ID（role>=3）",
            ),
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True, comment="审核时间"),
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
        tables = set(inspector.get_table_names())

    if "user_application_forms" in tables:
        cols = _column_names(inspector, "user_application_forms")
        # Idempotent: in case table existed but missing columns.
        if "reviewed_by" not in cols:
            op.add_column("user_application_forms", sa.Column("reviewed_by", sa.Integer(), nullable=True))
        if "reviewed_at" not in cols:
            op.add_column("user_application_forms", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))

        idx = _index_names(inspector, "user_application_forms")
        if "uq_user_application_forms_user_id" not in idx:
            op.create_index("uq_user_application_forms_user_id", "user_application_forms", ["user_id"], unique=True)
        if "ix_user_application_forms_status" not in idx:
            op.create_index("ix_user_application_forms_status", "user_application_forms", ["status"])
        if "ix_user_application_forms_created_at" not in idx:
            op.create_index("ix_user_application_forms_created_at", "user_application_forms", ["created_at"])

    #
    # user_messages
    #
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if "user_messages" not in tables:
        op.create_table(
            "user_messages",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                comment="接收消息的用户ID",
            ),
            sa.Column(
                "created_by",
                sa.Integer(),
                sa.ForeignKey("users.id"),
                nullable=True,
                comment="发送人用户ID（系统/管理员可为空）",
            ),
            sa.Column("batch_id", sa.String(length=36), nullable=True, comment="群发批次ID（用于撤回整批消息）"),
            sa.Column("title", sa.String(length=200), nullable=False, server_default=sa.text("'系统消息'"), comment="消息标题"),
            sa.Column("content", sa.String(length=5000), nullable=False, comment="消息内容"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column("read_at", sa.DateTime(timezone=True), nullable=True, comment="阅读时间"),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True, comment="撤回时间"),
            sa.Column("revoked_by", sa.Integer(), nullable=True, comment="撤回人用户ID（role=4）"),
        )
        inspector = inspect(bind)

    cols = _column_names(inspector, "user_messages")
    # Existing table might be created via create_all; add missing columns.
    if "batch_id" not in cols:
        op.add_column("user_messages", sa.Column("batch_id", sa.String(length=36), nullable=True))
    if "revoked_at" not in cols:
        op.add_column("user_messages", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    if "revoked_by" not in cols:
        op.add_column("user_messages", sa.Column("revoked_by", sa.Integer(), nullable=True))

    inspector = inspect(bind)
    idx = _index_names(inspector, "user_messages")
    if "ix_user_messages_user_id" not in idx:
        op.create_index("ix_user_messages_user_id", "user_messages", ["user_id"])
    if "ix_user_messages_batch_id" not in idx:
        op.create_index("ix_user_messages_batch_id", "user_messages", ["batch_id"])
    if "ix_user_messages_created_at" not in idx:
        op.create_index("ix_user_messages_created_at", "user_messages", ["created_at"])
    if "ix_user_messages_read_at" not in idx:
        op.create_index("ix_user_messages_read_at", "user_messages", ["read_at"])
    if "ix_user_messages_revoked_at" not in idx:
        op.create_index("ix_user_messages_revoked_at", "user_messages", ["revoked_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "user_messages" in tables:
        cols = _column_names(inspector, "user_messages")
        if "revoked_by" in cols:
            op.drop_column("user_messages", "revoked_by")
        if "revoked_at" in cols:
            op.drop_column("user_messages", "revoked_at")
        if "batch_id" in cols:
            op.drop_column("user_messages", "batch_id")

    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    if "user_application_forms" in tables:
        idx = _index_names(inspector, "user_application_forms")
        if "ix_user_application_forms_created_at" in idx:
            op.drop_index("ix_user_application_forms_created_at", table_name="user_application_forms")
        if "ix_user_application_forms_status" in idx:
            op.drop_index("ix_user_application_forms_status", table_name="user_application_forms")
        if "uq_user_application_forms_user_id" in idx:
            op.drop_index("uq_user_application_forms_user_id", table_name="user_application_forms")
        op.drop_table("user_application_forms")


