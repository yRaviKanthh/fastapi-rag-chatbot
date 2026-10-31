from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.routes import auth, document

from app.database import Base, engine

from app.models.user import User

from app.routes import chat

Base.metadata.create_all(bind=engine)


app = FastAPI(title="Doc Chat")


app.include_router(auth.router)

app.include_router(document.router)

app.include_router(chat.router)


STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/", include_in_schema=False)
def home():

    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():

    return {
        "message": "Backend is running"
    }
