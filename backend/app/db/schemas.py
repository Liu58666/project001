from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50, description="用户名")
    phone: str = Field(min_length=6, max_length=20, description="手机号")


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
    code: str = Field(min_length=4, max_length=10, description="验证码")

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserLogin(BaseModel):
    phone: str
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    role: int
    email: Optional[EmailStr] = None
    birthday: Optional[date] = None
    photo: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserAvatarOut(BaseModel):
    id: int
    photo: Optional[str] = None

    model_config = {"from_attributes": True}


class UserProfileOut(BaseModel):
    username: str
    phone: str
    email: Optional[EmailStr] = None
    birthday: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_expires_in: int
    refresh_expires_in: int
    username: str
    created_at: datetime
    email: Optional[EmailStr] = None
    birthday: Optional[date] = None
    photo: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    sub: Optional[str] = None
    type: Optional[str] = None
    role: Optional[int] = None
    roles: Optional[list[int]] = None


class UserProfileUpdate(BaseModel):
    username: Optional[str] = Field(
        default=None, min_length=3, max_length=50, description="用户名（可填可改，需唯一）"
    )
    email: Optional[EmailStr] = Field(default=None, description="邮箱（可填可改）")
    birthday: Optional[date] = Field(default=None, description="生日（YYYY-MM-DD）")


class AdminUserUpdate(BaseModel):
    """
    role==4 管理员更新用户字段的请求体
    """

    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    phone: Optional[str] = Field(default=None, min_length=6, max_length=20)
    email: Optional[EmailStr] = Field(default=None)
    birthday: Optional[date] = Field(default=None)
    photo: Optional[str] = Field(default=None, max_length=255, description="头像URL（如需手工指定）")
    is_active: Optional[bool] = Field(default=None)
    role: Optional[int] = Field(default=None, ge=0, le=10)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128, description="重置密码（可选）")


#
# Application form (one-time)
#

class ApplicationPreference(str, Enum):
    research = "科研"
    development = "开发"
    both = "均可"


class ApplicationStatus(int, Enum):
    pending = 0
    accepted = 1
    rejected = 2


class UserApplicationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="姓名")
    grade: str = Field(min_length=1, max_length=50, description="年级")
    age: int = Field(ge=0, le=200, description="年龄")
    major: str = Field(min_length=1, max_length=100, description="专业")
    school: str = Field(min_length=1, max_length=255, description="学校")
    preference: ApplicationPreference = Field(description="更倾向于：科研/开发/均可")
    experience: str = Field(min_length=1, max_length=5000, description="我的经历（纯文本）")
    message: Optional[str] = Field(default=None, max_length=2000, description="有没有什么想对我们说？")
    participated_before: bool = Field(description="之前是否有参与过我们的课程？（是/否）")


class UserApplicationOut(BaseModel):
    id: int
    user_id: int

    name: Optional[str] = None
    grade: Optional[str] = None
    age: Optional[int] = None
    major: Optional[str] = None
    school: Optional[str] = None
    preference: Optional[str] = None
    experience: Optional[str] = None
    message: Optional[str] = None
    participated_before: Optional[bool] = None

    status: int
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserApplicationAdminOut(UserApplicationOut):
    username: str = Field(description="用户名")
    phone: str = Field(description="手机号")


#
# System messages (in-app)
#

class ApplicationAcceptRequest(BaseModel):
    message: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="发送给申请人的确认信息（站内系统消息）。为空则使用默认文案。",
    )


class UserMessageOut(BaseModel):
    id: int
    user_id: int
    created_by: Optional[int] = None
    title: str
    content: str
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AdminBroadcastMessageRequest(BaseModel):
    title: str = Field(default="系统消息", max_length=200, description="消息标题")
    content: str = Field(min_length=1, max_length=5000, description="消息内容")
    roles: Optional[list[int]] = Field(default=None, description="目标用户 role 列表（支持多选）")
    user_ids: Optional[list[int]] = Field(default=None, description="目标用户ID列表（指定用户）")

    @model_validator(mode="after")
    def validate_targets(self):
        roles = self.roles or []
        user_ids = self.user_ids or []
        if len(roles) == 0 and len(user_ids) == 0:
            raise ValueError("Either roles or user_ids must be provided")
        return self


class AdminBroadcastMessageResponse(BaseModel):
    sent_count: int = Field(description="实际发送（写入站内信）的数量")
    recipient_count: int = Field(description="去重后的接收用户数量")
    batch_id: str = Field(description="群发批次ID（用于撤回）")


class AdminRevokeBroadcastResponse(BaseModel):
    revoked_count: int = Field(description="撤回的消息数量")
    batch_id: str = Field(description="群发批次ID")


class NewsBase(BaseModel):
    slug: str = Field(min_length=1, max_length=255)
    category: str = Field(default="News", max_length=50)
    published_at: date = Field(alias="publishedAt")
    title: str = Field(min_length=1, max_length=255)
    subtitle: str = Field(default="", max_length=500)
    author: str = Field(default="Company", max_length=100)
    content: list[str] = Field(min_length=1, description="段落数组")

    model_config = {"populate_by_name": True}


class NewsCreate(NewsBase):
    pass


class NewsImageItem(BaseModel):
    """新闻内容中的图片项"""
    url: str = Field(description="图片URL")
    position: int = Field(description="图片占位符索引，对应content中的[IMAGE:index]中的index")
    caption: str = Field(default="", description="图片说明")


class NewsOut(NewsBase):
    id: int
    cover_image: Optional[str] = Field(default=None, description="封面图片URL")
    images: list[NewsImageItem] = Field(default_factory=list, description="内容中的图片列表")

    model_config = {"from_attributes": True, "populate_by_name": True}


class SendCodeRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=20, description="手机号")


class SendCodeResponse(BaseModel):
    message: str = "Verification code sent successfully"
    resend_interval_seconds: int = Field(description="重发间隔（秒）")


class NewsImageBase(BaseModel):
    position: str = Field(
        min_length=1,
        max_length=50,
        description="图片位置：cover(封面), content(内容), thumbnail(缩略图), banner(横幅)等",
    )
    news_id: Optional[int] = Field(default=None, description="关联的新闻ID，可为空")


class NewsImageCreate(NewsImageBase):
    pass


class NewsImageOut(NewsImageBase):
    id: int
    cos_key: str = Field(description="腾讯云COS对象键")
    url: str = Field(description="完整访问URL")
    original_filename: str = Field(description="原始文件名")
    file_size: int = Field(description="文件大小（字节）")
    width: int = Field(description="图片宽度（像素）")
    height: int = Field(description="图片高度（像素）")
    caption: str = Field(default="", description="图片说明")
    uploaded_by: int = Field(description="上传用户ID")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NewsImageUploadResponse(BaseModel):
    """图片上传响应"""
    id: int
    url: str = Field(description="完整访问URL")
    position: str = Field(description="图片位置")
    news_id: Optional[int] = Field(default=None, description="关联的新闻ID")
    original_filename: str = Field(description="原始文件名")
    file_size: int = Field(description="文件大小（字节）")
    width: int = Field(description="图片宽度（像素）")
    height: int = Field(description="图片高度（像素）")
    created_at: datetime


#
# Resume / User images
#

class ResumeBase(BaseModel):
    real_name: str = Field(min_length=1, max_length=100, description="真实姓名")
    gender: Optional[str] = Field(default=None, max_length=10, description="性别：male/female/other")
    age: Optional[int] = Field(default=None, ge=0, le=200, description="年龄")
    address: Optional[str] = Field(default=None, max_length=500, description="地址")
    job_title: Optional[str] = Field(default=None, max_length=100, description="职位")
    department: Optional[str] = Field(default=None, max_length=100, description="部门")
    education: Optional[str] = Field(default=None, max_length=500, description="教育背景/学历")
    bio: list[str] = Field(
        default_factory=list,
        description="个人简介段落数组，可包含[IMAGE:0]等占位符",
    )
    is_public: bool = Field(default=True, description="是否公开展示")


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    real_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    gender: Optional[str] = Field(default=None, max_length=10)
    age: Optional[int] = Field(default=None, ge=0, le=200)
    address: Optional[str] = Field(default=None, max_length=500)
    job_title: Optional[str] = Field(default=None, max_length=100)
    department: Optional[str] = Field(default=None, max_length=100)
    education: Optional[str] = Field(default=None, max_length=500)
    bio: Optional[list[str]] = Field(default=None, description="个人简介段落数组")
    is_public: Optional[bool] = Field(default=None, description="是否公开展示")


class ResumeBioImageItem(BaseModel):
    """个人简介中的图片项（按上传顺序映射到[IMAGE:index]占位符）"""

    url: str = Field(description="图片URL")
    position: int = Field(description="占位符索引，对应bio中的[IMAGE:index]")
    caption: str = Field(default="", description="图片说明")


class UserImageOut(BaseModel):
    id: int
    user_id: int
    image_type: str
    cos_key: str
    url: str
    original_filename: str
    file_size: int
    width: int
    height: int
    caption: str = ""
    display_order: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserImageUploadResponse(BaseModel):
    id: int
    url: str
    image_type: str
    original_filename: str
    file_size: int
    width: int
    height: int
    caption: str = ""
    display_order: int = 0
    created_at: datetime


class ResumeOut(BaseModel):
    id: int
    user_id: int

    role: int
    real_name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    education: Optional[str] = None
    bio: list[str] = Field(default_factory=list)
    is_public: bool

    avatar_url: Optional[str] = None
    bio_images: list[ResumeBioImageItem] = Field(default_factory=list)
    certificates: list[UserImageOut] = Field(default_factory=list)
    projects: list[UserImageOut] = Field(default_factory=list)
    portfolios: list[UserImageOut] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeDirectoryItemOut(BaseModel):
    """
    简历目录项：
    - 始终返回基础信息（职务/真实姓名/部门/头像）
    - 若 is_public=True，则 resume 返回完整简历详情；否则 resume 为 None 且 private_hidden=True
    """

    user_id: int
    role: int
    real_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    is_public: bool
    private_hidden: bool = Field(description="是否隐藏了其它非公开内容")
    resume: Optional[ResumeOut] = None


class ResumePdfOut(BaseModel):
    id: int
    user_id: int

    cos_key: str
    url: str
    original_filename: str
    file_size: int

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminResumePdfOut(ResumePdfOut):
    username: str
    phone: str
    role: int


#
# Tasks / Submissions / Scoring
#


class AdminTaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="任务标题")
    content: str = Field(min_length=1, max_length=5000, description="任务内容（纯文本）")
    roles: Optional[list[int]] = Field(default=None, description="目标用户 role 列表（支持多选）")
    user_ids: Optional[list[int]] = Field(default=None, description="目标用户ID列表（指定用户）")

    @model_validator(mode="after")
    def validate_targets(self):
        roles = self.roles or []
        user_ids = self.user_ids or []
        if len(roles) == 0 and len(user_ids) == 0:
            raise ValueError("Either roles or user_ids must be provided")
        return self


class TaskOut(BaseModel):
    id: int
    title: str
    content: str
    created_by: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # populated by list endpoints (computed)
    recipient_count: Optional[int] = None

    model_config = {"from_attributes": True}


class TaskSubmissionUpsert(BaseModel):
    text_content: Optional[str] = Field(default=None, max_length=5000, description="提交内容（纯文本，可选）")
    suggestion: Optional[str] = Field(default=None, max_length=2000, description="建议（纯文本，可选）")


class TaskSubmissionImageOut(BaseModel):
    id: int
    submission_id: int
    cos_key: str
    url: str
    original_filename: str
    file_size: int
    width: int
    height: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskSubmissionOut(BaseModel):
    id: int
    task_id: int
    user_id: int
    text_content: Optional[str] = None
    suggestion: Optional[str] = None
    score: Optional[int] = None
    scored_by: Optional[int] = None
    scored_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    images: list[TaskSubmissionImageOut] = Field(default_factory=list, description="提交图片列表")

    model_config = {"from_attributes": True}


class TaskAssignedOut(TaskOut):
    my_submission: Optional[TaskSubmissionOut] = None


class TaskSubmissionImageUploadResponse(BaseModel):
    id: int
    url: str
    original_filename: str
    file_size: int
    width: int
    height: int
    created_at: datetime


class TaskScoreRequest(BaseModel):
    score: int = Field(ge=0, le=100, description="评分（0-100）")


class TaskSubmissionAdminOut(TaskSubmissionOut):
    username: str = Field(description="用户名")
    phone: str = Field(description="手机号")
