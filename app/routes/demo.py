import secrets
import time
from collections import deque
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User

from app.utils.hashing import hash_password

from app.utils.jwt_handler import create_access_token

from app.utils.document_loader import load_text

from app.utils.vector_store import create_embeddings


router = APIRouter()


DEMO_FILE = Path(__file__).resolve().parent.parent / "demo" / "sample_leave_policy.txt"

# Stops someone from creating thousands of demo accounts.
MAX_GUESTS_PER_HOUR = 200

_recent_guests = deque()


@router.post("/guest")
def guest(db: Session = Depends(get_db)):

    now = time.time()

    while _recent_guests and now - _recent_guests[0] > 3600:
        _recent_guests.popleft()

    if len(_recent_guests) >= MAX_GUESTS_PER_HOUR:

        raise HTTPException(
            status_code=429,
            detail="The demo is busy right now. Try again in a few minutes."
        )

    _recent_guests.append(now)

    email = f"guest-{secrets.token_hex(4)}@demo.local"

    user = User(
        email=email,
        hashed_password=hash_password(secrets.token_urlsafe(16))
    )

    db.add(user)

    db.commit()

    total_chunks = create_embeddings(
        load_text(str(DEMO_FILE)),
        email,
        DEMO_FILE.name
    )

    return {
        "access_token": create_access_token(data={"sub": email}),
        "token_type": "bearer",
        "email": email,
        "demo_file": DEMO_FILE.name,
        "chunks_created": total_chunks
    }
