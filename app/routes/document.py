from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)

import os

from app.utils.document_loader import load_text

from app.utils.vector_store import create_embeddings

from app.utils.jwt_handler import get_current_user

from app.models.user import User


router = APIRouter()


UPLOAD_FOLDER = "uploads"

MAX_UPLOAD_BYTES = 2 * 1024 * 1024

ALLOWED_EXTENSIONS = (".txt", ".pdf")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):

    filename = os.path.basename(file.filename or "")

    if not filename.lower().endswith(ALLOWED_EXTENSIONS):

        raise HTTPException(
            status_code=400,
            detail="Only TXT and PDF files are supported."
        )

    content = await file.read()

    if len(content) > MAX_UPLOAD_BYTES:

        raise HTTPException(
            status_code=413,
            detail="File is too large. The limit is 2 MB."
        )

    user_folder = os.path.join(UPLOAD_FOLDER, current_user.email)

    os.makedirs(user_folder, exist_ok=True)

    file_path = os.path.join(user_folder, filename)

    with open(file_path, "wb") as buffer:

        buffer.write(content)

    try:

        extracted_text = load_text(file_path)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Could not read this file. Try another one."
        )

    total_chunks = create_embeddings(
        extracted_text,
        current_user.email,
        filename
    )

    return {
        "filename": filename,
        "uploaded_by": current_user.email,
        "chunks_created": total_chunks,
        "message": "Embeddings created successfully"
    }
