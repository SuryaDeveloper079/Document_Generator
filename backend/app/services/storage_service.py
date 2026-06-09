import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from typing import Optional
from app.core.config import settings

_s3_kwargs = {
    "aws_access_key_id": settings.S3_ACCESS_KEY_ID or "minioadmin",
    "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY or "minioadmin",
    "region_name": settings.S3_REGION,
    "config": Config(signature_version="s3v4"),
}
if settings.S3_ENDPOINT_URL:
    _s3_kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL

try:
    s3_client = boto3.client("s3", **_s3_kwargs)
except Exception:
    s3_client = None


class StorageService:
    bucket = settings.S3_BUCKET_NAME

    @classmethod
    def upload_text(cls, content: str, key: str, content_type: str = "text/markdown") -> str:
        if not s3_client:
            return key
        try:
            s3_client.put_object(Bucket=cls.bucket, Key=key, Body=content.encode("utf-8"), ContentType=content_type)
        except Exception:
            pass
        return key

    @classmethod
    def upload_bytes(cls, data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        if not s3_client:
            return key
        try:
            s3_client.put_object(Bucket=cls.bucket, Key=key, Body=data, ContentType=content_type)
        except Exception:
            pass
        return key

    @classmethod
    def get_presigned_url(cls, key: str, expires: int = 3600) -> Optional[str]:
        if not s3_client:
            return None
        try:
            return s3_client.generate_presigned_url("get_object", Params={"Bucket": cls.bucket, "Key": key}, ExpiresIn=expires)
        except Exception:
            return None

    @classmethod
    def delete(cls, key: str) -> None:
        if not s3_client:
            return
        try:
            s3_client.delete_object(Bucket=cls.bucket, Key=key)
        except Exception:
            pass

    @classmethod
    def document_key(cls, project_id: str, doc_id: str, fmt: str = "md") -> str:
        return f"documents/{project_id}/{doc_id}/content.{fmt}"

    @classmethod
    def diagram_key(cls, doc_id: str, diagram_id: str, fmt: str = "svg") -> str:
        return f"diagrams/{doc_id}/{diagram_id}.{fmt}"

    @classmethod
    def source_key(cls, project_id: str, filename: str) -> str:
        return f"sources/{project_id}/{filename}"


storage = StorageService()
