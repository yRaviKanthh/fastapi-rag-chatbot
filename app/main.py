from fastapi import FastAPI

from app.routes import auth, document

from app.database import Base, engine

from app.models.user import User

from app.routes import chat

Base.metadata.create_all(bind=engine)


app = FastAPI()


app.include_router(auth.router)

app.include_router(document.router)

app.include_router(chat.router)

@app.get("/")
def home():

    return {
        "message": "Backend is running"
    }