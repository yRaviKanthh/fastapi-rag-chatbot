from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

import shutil
import os

from app.utils.document_loader import load_text

from app.utils.vector_store import create_embeddings

from app.utils.jwt_handler import get_current_user

from app.models.user import User


router = APIRouter()


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):

    user_folder = f"{UPLOAD_FOLDER}/{current_user.email}"

    os.makedirs(user_folder, exist_ok=True)

    file_path = f"{user_folder}/{file.filename}"

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(file.file, buffer)

    extracted_text = load_text(file_path)

    total_chunks = create_embeddings(extracted_text)

    return {
        "filename": file.filename,
        "uploaded_by": current_user.email,
        "chunks_created": total_chunks,
        "message": "Embeddings created successfully"
    }