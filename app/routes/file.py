from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.middleware.decorator import rate_limit
from config import settings
from app.controllers.file import FileController
from app.database.client import get_db
from app.dto import FileResponse

router = APIRouter()


@router.post("/file/upload")
@rate_limit(
    max_requests=settings.RATE_LIMIT_MAX_REQUESTS + 10,
    window=settings.RATE_LIMIT_WINDOW,
)
def agent_upload(
    request: Request, file: UploadFile = File(None), db: Session = Depends(get_db)
) -> FileResponse:
    file_controller = FileController(db)
    return file_controller.upload_file(file, None)
