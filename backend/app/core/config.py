from functools import lru_cache
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    app_name: str = "AuthService"
    debug: bool = False

    # Database
    database_url: AnyUrl = Field(
        ...,
        description="MySQL URL, e.g. mysql+pymysql://user:pass@host:3306/dbname",
    )

    # JWT
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Security
    bcrypt_rounds: int = 12

    # SMS Service - 腾讯云短信服务配置
    # 凭据只从环境变量 / .env 注入，切勿在源码中写死默认值
    sms_secret_id: str = Field(default="", description="腾讯云 SecretId (访问密钥 ID)")
    sms_secret_key: str = Field(default="", description="腾讯云 SecretKey (访问密钥 Key)")
    sms_sdk_app_id: str = Field(default="", description="腾讯云 SmsSdkAppId (短信应用 ID)")
    sms_sign_name: str = Field(default="", description="短信签名内容 (如: DAIL Tech)")
    sms_template_id: str = Field(default="", description="短信模板 ID")
    sms_region: str = Field(default="ap-guangzhou", description="腾讯云服务区域 (推荐使用 ap-guangzhou)")

    # Verification Code
    verification_code_length: int = 6
    verification_code_expire_minutes: int = 5
    verification_code_resend_interval_seconds: int = 60

    # Tencent Cloud COS (Object Storage) Configuration
    cos_secret_id: str = Field(default="", description="腾讯云 COS SecretId")
    cos_secret_key: str = Field(default="", description="腾讯云 COS SecretKey")
    cos_region: str = Field(default="ap-guangzhou", description="腾讯云 COS 区域")
    cos_bucket: str = Field(default="news-1327732770", description="腾讯云 COS 存储桶名称")
    cos_domain: str = Field(
        default="news-1327732770.cos.ap-guangzhou.myqcloud.com",
        description="腾讯云 COS 域名"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

