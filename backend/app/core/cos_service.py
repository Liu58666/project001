"""
腾讯云 COS (对象存储) 服务
用于上传和管理新闻图片
"""
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError

from app.core.config import get_settings


class COSService:
    """腾讯云 COS 服务类"""

    def __init__(self):
        settings = get_settings()
        self.secret_id = settings.cos_secret_id
        self.secret_key = settings.cos_secret_key
        self.region = settings.cos_region
        self.bucket = settings.cos_bucket
        self.domain = settings.cos_domain
        self.enabled = settings.cos_enabled

        self.client = None
        if not self.enabled:
            return
        if not all([self.secret_id, self.secret_key, self.bucket, self.domain]):
            raise RuntimeError("COS_ENABLED=true requires COS_SECRET_ID, COS_SECRET_KEY, COS_BUCKET, and COS_DOMAIN")

        config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Scheme="https",
        )
        self.client = CosS3Client(config)

    def _ensure_enabled(self) -> None:
        if not self.enabled or self.client is None:
            raise RuntimeError("COS service is disabled")

    def _generate_object_key(
        self,
        namespace: str,
        category: str,
        original_filename: str,
        *,
        user_id: int | None = None,
    ) -> str:
        """
        生成 COS 对象键（文件路径）
        
        Args:
            namespace: 业务命名空间（news/users）
            category: 业务类别（news: position; users: image_type）
            original_filename: 原始文件名
            user_id: 当 namespace=users 时必填
            
        Returns:
            COS 对象键
        """
        # 获取文件扩展名
        ext = Path(original_filename).suffix.lower() or ".jpg"
        
        # 生成唯一文件名
        unique_id = uuid.uuid4().hex
        now = datetime.now()
        
        if namespace == "news":
            # 格式：news/{position}/{year}/{month}/{uuid}.{ext}
            object_key = f"news/{category}/{now.year}/{now.month:02d}/{unique_id}{ext}"
        elif namespace == "users":
            if user_id is None:
                raise ValueError("user_id is required when namespace is 'users'")
            # 格式：users/{user_id}/{image_type}/{year}/{month}/{uuid}.{ext}
            object_key = f"users/{user_id}/{category}/{now.year}/{now.month:02d}/{unique_id}{ext}"
        else:
            # fallback: {namespace}/{category}/{year}/{month}/{uuid}.{ext}
            object_key = f"{namespace}/{category}/{now.year}/{now.month:02d}/{unique_id}{ext}"
        
        return object_key

    def upload_image(
        self,
        file_content: bytes,
        position: str,
        original_filename: str,
        max_size: Optional[tuple[int, int]] = None,
        quality: int = 85,
    ) -> dict:
        """
        上传图片到腾讯云 COS
        
        Args:
            file_content: 图片文件内容（字节）
            position: 图片位置（如：cover, content, thumbnail, banner 等）
            original_filename: 原始文件名
            max_size: 可选，最大尺寸 (width, height)，如果提供会自动压缩
            quality: JPEG 质量（1-100），默认 85
            
        Returns:
            dict: {
                'url': 完整访问 URL,
                'key': COS 对象键,
                'size': 文件大小（字节）,
                'width': 图片宽度（像素）,
                'height': 图片高度（像素）
            }
            
        Raises:
            ValueError: 如果图片处理失败
            CosClientError: COS 客户端错误
            CosServiceError: COS 服务错误
        """
        try:
            self._ensure_enabled()
            # 处理图片（如果需要压缩）
            image = Image.open(BytesIO(file_content))
            original_format = image.format or "JPEG"
            width, height = image.size
            
            # 如果指定了最大尺寸，进行压缩
            if max_size:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                width, height = image.size
            
            # 转换为 RGB（如果是 RGBA 或其他格式）
            if image.mode in ("RGBA", "LA", "P"):
                # 创建白色背景
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")
            
            # 保存为字节流
            output = BytesIO()
            image.save(output, format="JPEG", quality=quality, optimize=True)
            output.seek(0)
            processed_content = output.getvalue()
            
            # 生成对象键（新闻图片）
            object_key = self._generate_object_key("news", position, original_filename)
            
            # 上传到 COS
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=processed_content,
                Key=object_key,
                ContentType="image/jpeg",
            )
            
            # 构建完整 URL
            url = f"https://{self.domain}/{object_key}"
            
            return {
                "url": url,
                "key": object_key,
                "size": len(processed_content),
                "width": width,
                "height": height,
            }
            
        except Exception as e:
            if isinstance(e, (CosClientError, CosServiceError)):
                raise
            raise ValueError(f"图片处理失败: {str(e)}")

    def upload_user_image(
        self,
        file_content: bytes,
        user_id: int,
        image_type: str,
        original_filename: str,
        max_size: Optional[tuple[int, int]] = None,
        quality: int = 85,
    ) -> dict:
        """
        上传用户图片到腾讯云 COS

        对象键格式：users/{user_id}/{image_type}/{year}/{month}/{uuid}.{ext}
        """
        # 复用同样的处理逻辑
        try:
            self._ensure_enabled()
            image = Image.open(BytesIO(file_content))
            width, height = image.size

            if max_size:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                width, height = image.size

            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            output = BytesIO()
            image.save(output, format="JPEG", quality=quality, optimize=True)
            output.seek(0)
            processed_content = output.getvalue()

            object_key = self._generate_object_key(
                "users",
                image_type,
                original_filename,
                user_id=user_id,
            )

            self.client.put_object(
                Bucket=self.bucket,
                Body=processed_content,
                Key=object_key,
                ContentType="image/jpeg",
            )

            url = f"https://{self.domain}/{object_key}"
            return {
                "url": url,
                "key": object_key,
                "size": len(processed_content),
                "width": width,
                "height": height,
            }
        except Exception as e:
            if isinstance(e, (CosClientError, CosServiceError)):
                raise
            raise ValueError(f"图片处理失败: {str(e)}")

    def upload_task_submission_image(
        self,
        file_content: bytes,
        task_id: int,
        user_id: int,
        original_filename: str,
        max_size: Optional[tuple[int, int]] = None,
        quality: int = 85,
    ) -> dict:
        """
        上传任务提交图片到腾讯云 COS

        对象键格式：tasks/{task_id}/{user_id}/{year}/{month}/{uuid}.{ext}
        """
        try:
            self._ensure_enabled()
            image = Image.open(BytesIO(file_content))
            width, height = image.size

            if max_size:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                width, height = image.size

            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            output = BytesIO()
            image.save(output, format="JPEG", quality=quality, optimize=True)
            output.seek(0)
            processed_content = output.getvalue()

            ext = Path(original_filename).suffix.lower() or ".jpg"
            unique_id = uuid.uuid4().hex
            now = datetime.now()
            object_key = f"tasks/{int(task_id)}/{int(user_id)}/{now.year}/{now.month:02d}/{unique_id}{ext}"

            self.client.put_object(
                Bucket=self.bucket,
                Body=processed_content,
                Key=object_key,
                ContentType="image/jpeg",
            )

            url = f"https://{self.domain}/{object_key}"
            return {
                "url": url,
                "key": object_key,
                "size": len(processed_content),
                "width": width,
                "height": height,
            }
        except Exception as e:
            if isinstance(e, (CosClientError, CosServiceError)):
                raise
            raise ValueError(f"图片处理失败: {str(e)}")

    def upload_user_pdf(
        self,
        file_content: bytes,
        user_id: int,
        original_filename: str,
    ) -> dict:
        """
        上传用户 PDF 简历到腾讯云 COS（不做图片处理/压缩）。

        对象键格式：users/{user_id}/resume_pdf/{year}/{month}/{uuid}.pdf
        """
        try:
            self._ensure_enabled()
            # Ensure .pdf suffix
            filename = original_filename or "resume.pdf"
            if not Path(filename).suffix:
                filename = f"{filename}.pdf"

            object_key = self._generate_object_key(
                "users",
                "resume_pdf",
                filename,
                user_id=int(user_id),
            )

            self.client.put_object(
                Bucket=self.bucket,
                Body=file_content,
                Key=object_key,
                ContentType="application/pdf",
            )

            url = f"https://{self.domain}/{object_key}"
            return {
                "url": url,
                "key": object_key,
                "size": len(file_content),
            }
        except Exception as e:
            if isinstance(e, (CosClientError, CosServiceError)):
                raise
            raise ValueError(f"文件上传失败: {str(e)}")

    def delete_image(self, object_key: str) -> bool:
        """
        从 COS 删除图片
        
        Args:
            object_key: COS 对象键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            self._ensure_enabled()
            self.client.delete_object(Bucket=self.bucket, Key=object_key)
            return True
        except (CosClientError, CosServiceError) as exc:
            status_code = getattr(exc, "get_status_code", lambda: None)()
            if int(status_code or 0) == 404:
                return True
            return False
        except RuntimeError:
            return False

    def get_image_url(self, object_key: str) -> str:
        """
        根据对象键生成完整 URL
        
        Args:
            object_key: COS 对象键
            
        Returns:
            完整访问 URL
        """
        return f"https://{self.domain}/{object_key}"


# 全局 COS 服务实例
cos_service = COSService()


