import uuid

from fastapi import UploadFile, HTTPException

from src.app.core.s3 import s3_client, S3_BUCKET

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


async def upload_post_image(file: UploadFile, post_id: uuid.UUID):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid image type")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(400, "Image too large")

    ext = file.filename.split(".")[-1]
    object_key = f"posts/{post_id}/{uuid.uuid4()}.{ext}"

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=object_key,
        Body=content,
        ContentType=file.content_type,
    )

    return object_key


def delete_image(object_key: str):
    s3_client.delete_object(
        Bucket=S3_BUCKET,
        Key=object_key
    )


def generate_presigned_url(object_key: str) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": object_key},
        ExpiresIn=3600,
    )
