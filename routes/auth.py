from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas.user import UserCreate
from utils.security import hash_password, verify_password
from utils.jwt import create_access_token

router = APIRouter(prefix="/auth")

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email")

    # NEW CHECK
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "user_id": user.id,
        "role_id": user.role_id
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(400, "Email already exists")

    hashed_password = hash_password(user.password)

    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password
        # role_id and department_id will be default
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully"}