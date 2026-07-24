"""
短信服务模块 - 腾讯云短信服务实现
"""
import logging
from typing import Optional

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20210111 import sms_client, models

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_sms_code(phone: str, code: str) -> bool:
    """
    使用腾讯云短信服务发送验证码

    Args:
        phone: 手机号（支持 +86 前缀或纯数字）
        code: 验证码

    Returns:
        bool: 发送是否成功

    需要配置的环境变量：
    - SMS_SECRET_ID: 腾讯云 SecretId
    - SMS_SECRET_KEY: 腾讯云 SecretKey
    - SMS_SDK_APP_ID: 短信应用 ID
    - SMS_SIGN_NAME: 短信签名内容
    - SMS_TEMPLATE_ID: 短信模板 ID
    - SMS_REGION: 服务区域（默认 ap-guangzhou）
    """
    masked_phone = _mask_phone(phone)

    if not settings.sms_enabled:
        logger.info("SMS disabled; verification code generated for %s", masked_phone)
        return True

    # 检查配置是否完整
    if not all([
        settings.sms_secret_id,
        settings.sms_secret_key,
        settings.sms_sdk_app_id,
        settings.sms_sign_name,
        settings.sms_template_id,
    ]):
        logger.error(
            "SMS service configuration incomplete. Please check .env file for SMS_* settings."
        )
        return False

    try:
        # 实例化认证对象
        cred = credential.Credential(settings.sms_secret_id, settings.sms_secret_key)

        # 实例化 http 选项
        http_profile = HttpProfile()
        http_profile.reqMethod = "POST"
        http_profile.reqTimeout = 30
        http_profile.endpoint = "sms.tencentcloudapi.com"

        # 实例化 client 选项
        client_profile = ClientProfile()
        client_profile.signMethod = "HmacSHA256"
        client_profile.httpProfile = http_profile

        # 实例化 SMS 客户端
        client = sms_client.SmsClient(cred, settings.sms_region, client_profile)

        # 实例化请求对象
        req = models.SendSmsRequest()

        # 格式化手机号（确保有 +86 前缀）
        if not phone.startswith("+"):
            phone = f"+86{phone}"

        # 设置请求参数
        req.SmsSdkAppId = settings.sms_sdk_app_id
        req.SignName = settings.sms_sign_name
        req.TemplateId = settings.sms_template_id
        req.PhoneNumberSet = [phone]
        
        # 模板参数：根据模板内容设置
        # 常见情况：
        # 1. 单参数模板："您的验证码是{1}" -> [code]
        # 2. 双参数模板："您的验证码是{1}，有效期{2}分钟" -> [code, str(expire_minutes)]
        # 请根据你的模板内容调整参数数量
        expire_minutes = settings.verification_code_expire_minutes
        
        # 默认使用单参数（仅验证码），如果模板需要两个参数，取消下面的注释
        req.TemplateParamSet = [code]
        # 如果模板需要两个参数（验证码+过期时间），使用下面这行：
        # req.TemplateParamSet = [code, str(expire_minutes)]

        # 发送请求
        resp = client.SendSms(req)

        # 检查响应
        if resp.SendStatusSet and len(resp.SendStatusSet) > 0:
            status = resp.SendStatusSet[0]
            if status.Code == "Ok":
                logger.info("SMS sent successfully to %s", masked_phone)
                return True
            else:
                logger.error(
                    "Failed to send SMS to %s: Code=%s, Message=%s",
                    masked_phone,
                    status.Code,
                    status.Message,
                )
                return False
        else:
            logger.error(f"Unexpected SMS response format: {resp}")
            return False

    except TencentCloudSDKException as e:
        logger.error("TencentCloud SDK error when sending SMS to %s: %s", masked_phone, e)
        return False
    except Exception as e:
        logger.error("Unexpected error when sending SMS to %s: %s", masked_phone, e, exc_info=True)
        return False


def _mask_phone(phone: str) -> str:
    raw = str(phone or "")
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) <= 4:
        return "***"
    return f"{digits[:3]}****{digits[-4:]}"

