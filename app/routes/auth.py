from fastapi import APIRouter, Depends, HTTPException, Security

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User

from app.schemas.user import UserCreate, UserLogin

from app.utils.hashing import (
    hash_password,
    verify_password
)

from app.utils.jwt_handler import (
    create_access_token,
    get_current_user
)


router = APIRouter()


@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_pwd = hash_password(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_pwd
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password"
        )

    valid_password = verify_password(
        form_data.password,
        existing_user.hashed_password
    )

    if not valid_password:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={"sub": existing_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/profile")
def profile(
    current_user: User = Depends(get_current_user)
):

    return {
        "email": current_user.email
    }