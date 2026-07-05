from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_phone", "phone", unique=True),
        Index("ix_users_username", "username", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    role: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
        doc="0=normal, 1/2/3 elevated (3 highest)",
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    photo: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class UserApplicationForm(Base):
    __tablename__ = "user_application_forms"
    __table_args__ = (
        Index("uq_user_application_forms_user_id", "user_id", unique=True),
        Index("ix_user_application_forms_status", "status"),
        Index("ix_user_application_forms_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="关联的用户ID（一对一：同一用户只能提交一次）",
    )

    # 表单字段（拒绝时会清空，所以都允许为 NULL）
    name: Mapped[str | None] = mapped_column(String(100), nullable=True, doc="姓名")
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True, doc="年级")
    age: Mapped[int | None] = mapped_column(Integer, nullable=True, doc="年龄")
    major: Mapped[str | None] = mapped_column(String(100), nullable=True, doc="专业")
    school: Mapped[str | None] = mapped_column(String(255), nullable=True, doc="学校")
    preference: Mapped[str | None] = mapped_column(
        String(20), nullable=True, doc="更倾向于：科研/开发/均可"
    )
    experience: Mapped[str | None] = mapped_column(String(5000), nullable=True, doc="我的经历（纯文本）")
    message: Mapped[str | None] = mapped_column(String(2000), nullable=True, doc="有没有什么想对我们说？")
    participated_before: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, doc="之前是否有参与过我们的课程？"
    )

    # 0=pending(待审核), 1=accepted(已接受), 2=rejected(已拒绝且已清空数据)
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0", doc="审核状态"
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, doc="审核人用户ID（role>=3）"
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="审核时间"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class UserMessage(Base):
    __tablename__ = "user_messages"
    __table_args__ = (
        Index("ix_user_messages_user_id", "user_id"),
        Index("ix_user_messages_batch_id", "batch_id"),
        Index("ix_user_messages_created_at", "created_at"),
        Index("ix_user_messages_read_at", "read_at"),
        Index("ix_user_messages_revoked_at", "revoked_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, doc="接收消息的用户ID"
    )
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, doc="发送人用户ID（系统/管理员可为空）"
    )

    batch_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True, doc="群发批次ID（用于撤回整批消息）"
    )

    title: Mapped[str] = mapped_column(
        String(200), nullable=False, default="系统消息", server_default="系统消息", doc="消息标题"
    )
    content: Mapped[str] = mapped_column(String(5000), nullable=False, doc="消息内容")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, doc="阅读时间")
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, doc="撤回时间")
    revoked_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, doc="撤回人用户ID（role=4）"
    )


class UserResume(Base):
    __tablename__ = "user_resumes"
    __table_args__ = (
        Index("uq_user_resumes_user_id", "user_id", unique=True),
        Index("ix_user_resumes_is_public", "is_public"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, doc="关联的用户ID（一对一）"
    )

    real_name: Mapped[str] = mapped_column(String(100), nullable=False, doc="真实姓名")
    gender: Mapped[str | None] = mapped_column(
        String(10), nullable=True, doc="性别：male/female/other"
    )
    age: Mapped[int | None] = mapped_column(Integer, nullable=True, doc="年龄")
    address: Mapped[str | None] = mapped_column(String(500), nullable=True, doc="地址")
    role: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
        doc="冗余字段：与 users.role 保持一致，便于简历侧查询/展示",
    )
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, doc="联系电话（与 users.phone 同步）")
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, doc="邮箱（与 users.email 同步）")
    job_title: Mapped[str | None] = mapped_column(String(100), nullable=True, doc="职位")
    department: Mapped[str | None] = mapped_column(String(100), nullable=True, doc="部门")
    education: Mapped[str | None] = mapped_column(String(500), nullable=True, doc="教育背景/学历")
    # list[str] as JSON paragraphs; can include placeholders like [IMAGE:0]
    bio: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, doc="个人简介段落数组（可含图片占位符）")

    is_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1", doc="是否公开展示"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class UserResumePDF(Base):
    __tablename__ = "user_resume_pdfs"
    __table_args__ = (
        Index("uq_user_resume_pdfs_user_id", "user_id", unique=True),
        Index("ix_user_resume_pdfs_updated_at", "updated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="关联的用户ID（一对一：同一用户仅保留最新一份PDF简历）",
    )

    cos_key: Mapped[str] = mapped_column(String(500), nullable=False, doc="腾讯云COS对象键（文件路径）")
    url: Mapped[str] = mapped_column(String(1000), nullable=False, doc="完整访问URL（公开直链）")
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False, doc="原始文件名")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, doc="文件大小（字节）")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class UserImage(Base):
    __tablename__ = "user_images"
    __table_args__ = (
        Index("ix_user_images_user_id", "user_id"),
        Index("ix_user_images_image_type", "image_type"),
        Index("ix_user_images_display_order", "display_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, doc="关联的用户ID"
    )
    image_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="图片类型：avatar/certificate/project/portfolio/bio 等",
    )

    cos_key: Mapped[str] = mapped_column(String(500), nullable=False, doc="腾讯云COS对象键（文件路径）")
    url: Mapped[str] = mapped_column(String(1000), nullable=False, doc="完整访问URL")
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False, doc="原始文件名")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, doc="文件大小（字节）")
    width: Mapped[int] = mapped_column(Integer, nullable=False, doc="图片宽度（像素）")
    height: Mapped[int] = mapped_column(Integer, nullable=False, doc="图片高度（像素）")
    caption: Mapped[str] = mapped_column(
        String(500), nullable=False, default="", server_default="", doc="图片说明/标题"
    )
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0", doc="展示顺序（越小越靠前）"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class VerificationCode(Base):
    __tablename__ = "verification_codes"
    __table_args__ = (Index("ix_verification_codes_phone", "phone"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class News(Base):
    __tablename__ = "news"
    __table_args__ = (Index("ix_news_slug", "slug", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="News", server_default="News")
    published_at: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(500), nullable=False, default="", server_default="")
    author: Mapped[str] = mapped_column(String(100), nullable=False, default="Company", server_default="Company")
    # list[str] as JSON
    content: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_tokens_user_id", "user_id"),
        Index("ix_refresh_tokens_expires_at", "expires_at"),
        Index("uq_refresh_tokens_token_hash", "token_hash", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Store a one-way hash of the refresh token (never store the raw token)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Optional self-reference to support rotation chain tracking
    replaced_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("refresh_tokens.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class NewsImage(Base):
    __tablename__ = "news_images"
    __table_args__ = (
        Index("ix_news_images_news_id", "news_id"),
        Index("ix_news_images_position", "position"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int | None] = mapped_column(
        ForeignKey("news.id", ondelete="CASCADE"), nullable=True, doc="关联的新闻ID，可为空（未关联时）"
    )
    position: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="图片位置：cover(封面), content(内容), thumbnail(缩略图), banner(横幅)等",
    )
    cos_key: Mapped[str] = mapped_column(
        String(500), nullable=False, doc="腾讯云COS对象键（文件路径）"
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False, doc="完整访问URL")
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False, doc="原始文件名")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, doc="文件大小（字节）")
    width: Mapped[int] = mapped_column(Integer, nullable=False, doc="图片宽度（像素）")
    height: Mapped[int] = mapped_column(Integer, nullable=False, doc="图片高度（像素）")
    caption: Mapped[str] = mapped_column(
        String(500), nullable=False, default="", server_default="", doc="图片说明"
    )
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, doc="上传用户ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_created_by", "created_by"),
        Index("ix_tasks_published_at", "published_at"),
        Index("ix_tasks_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, doc="任务标题")
    content: Mapped[str] = mapped_column(String(5000), nullable=False, doc="任务内容（纯文本）")

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        doc="创建人用户ID（role in {3,4}）",
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="发布时间（可为空）"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class TaskRecipient(Base):
    __tablename__ = "task_recipients"
    __table_args__ = (
        Index("uq_task_recipients_task_id_user_id", "task_id", "user_id", unique=True),
        Index("ix_task_recipients_task_id", "task_id"),
        Index("ix_task_recipients_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        doc="任务ID",
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="接收者用户ID（发布时快照）",
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), doc="指派时间"
    )


class TaskSubmission(Base):
    __tablename__ = "task_submissions"
    __table_args__ = (
        Index("uq_task_submissions_task_id_user_id", "task_id", "user_id", unique=True),
        Index("ix_task_submissions_task_id", "task_id"),
        Index("ix_task_submissions_user_id", "user_id"),
        Index("ix_task_submissions_updated_at", "updated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        doc="任务ID",
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="提交者用户ID",
    )

    text_content: Mapped[str | None] = mapped_column(
        String(5000), nullable=True, doc="提交内容（纯文本）"
    )
    suggestion: Mapped[str | None] = mapped_column(
        String(2000), nullable=True, doc="建议（纯文本）"
    )

    score: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True, doc="评分（0-100，role>=3）"
    )
    scored_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, doc="评分人用户ID（role>=3）"
    )
    scored_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, doc="评分时间"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class TaskSubmissionImage(Base):
    __tablename__ = "task_submission_images"
    __table_args__ = (
        Index("ix_task_submission_images_submission_id", "submission_id"),
        Index("ix_task_submission_images_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("task_submissions.id", ondelete="CASCADE"),
        nullable=False,
        doc="关联的提交ID",
    )
    cos_key: Mapped[str] = mapped_column(String(500), nullable=False, doc="腾讯云COS对象键（文件路径）")
    url: Mapped[str] = mapped_column(String(1000), nullable=False, doc="完整访问URL")
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False, doc="原始文件名")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, doc="文件大小（字节）")
    width: Mapped[int] = mapped_column(Integer, nullable=False, doc="图片宽度（像素）")
    height: Mapped[int] = mapped_column(Integer, nullable=False, doc="图片高度（像素）")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )