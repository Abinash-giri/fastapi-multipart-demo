import boto3
import os
from fastapi import UploadFile

s3 = boto3.client("s3")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

async def upload_to_s3(file: UploadFile):
    content = await file.read()

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file.filename,
        Body=content
    )

    return f"s3://{BUCKET_NAME}/{file.filename}"
