from fastapi import APIRouter, UploadFile, File
from app.services.s3service import upload_to_s3

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    file_url = await upload_to_s3(file)

    return {
        "filename": file.filename,
        "s3_url": file_url
    }
