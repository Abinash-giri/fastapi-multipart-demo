import sys
import traceback
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from mangum import Mangum
import boto3
from datetime import datetime, timezone
import os
from typing import List
import logging
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s || %(levelname)s || %(name)s || %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("fastapi-multipart-demo")

app = FastAPI()
handler = Mangum(app)

# ===== CONFIG =====
load_dotenv()
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

s3_client = boto3.client("s3", region_name=AWS_REGION)

# ===== HEALTH CHECK =====

@app.get("/health")
def health():
    logger.info("Health check endpoint called.")
    return {"status": "ok"}


# ===== FILE UPLOAD ENDPOINT =====

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts file uploads of any format and uploads them to S3.
    """
    logger.info(f"Received file upload request: {file.filename}")
    try:
        # Generate unique file key
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        file_key = f"uploads/{timestamp}_{unique_id}_{file.filename}"

        # Read file bytes
        file_bytes = await file.read()

        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=file_key,
            Body=file_bytes,
            ContentType=file.content_type
        )

        logger.info(f"File uploaded: {file.filename} as {file_key} to bucket {S3_BUCKET}")
        return {
            "message": "File uploaded successfully",
            "file_name": file.filename,
            "s3_key": file_key,
            "bucket": S3_BUCKET
        }

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error uploading file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== MULTIPLE FILE UPLOAD =====

@app.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Accepts multiple files and uploads them to S3
    """
    logger.info(f"Received multiple file upload request: {[file.filename for file in files]}")
    upload_results = []

    for file in files:
        try:
            unique_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            file_key = f"uploads/{timestamp}_{unique_id}_{file.filename}"

            content = await file.read()

            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=file_key,
                Body=content,
                ContentType=file.content_type
            )

            logger.info(f"File uploaded: {file.filename} as {file_key} to bucket {S3_BUCKET}")
            upload_results.append({
                "file_name": file.filename,
                "s3_key": file_key,
                "status": "uploaded"
            })

        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error uploading file {file.filename}: {e}")
            upload_results.append({
                "file_name": file.filename,
                "status": "failed",
                "error": str(e)
            })

    return upload_results


# ===== LAMBDA HANDLER =====
def lambda_handler(event, context):
    print("EVENT: ", event)
    print("Lambda handler triggered")
    logger.info("Logger is working!")

    return handler(event, context)

#handler = Mangum(app)
#handler = custom_handler

