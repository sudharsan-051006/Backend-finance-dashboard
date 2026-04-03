from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Category
from schemas.user import UserCreate, UserUpdate
from utils.dependencies import get_current_user, require_role
from utils.roles import ADMIN, ANALYST, Viewer as USER
from models import Department
from utils.security import hash_password
from models import Role

router = APIRouter(prefix="/users")

@router.post("/")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role_id != ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    if not user.name or len(user.name.strip()) == 0:
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    if not user.password:
        raise HTTPException(status_code=400, detail="Password is required")

    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    if len(user.password) > 15:
        raise HTTPException(status_code=400, detail="Password must not exceed 15 characters")

    if not user.role_id or user.role_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid role_id")

    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if not user.department_id or user.department_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid department_id")


    dept = db.query(Department).filter(Department.id == user.department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    db_user = User(
        name=user.name.strip(),
        email=user.email.strip(),
        password=user.password,  # secure
        role_id=user.role_id,
        department_id=user.department_id,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/get-all")
def get_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    #  Admin -> all users
    if current_user.role_id == ADMIN:
        return db.query(User).all()

    #  Analyst -> only same department users
    if current_user.role_id == ANALYST:
        return db.query(User).filter(
            User.department_id == current_user.department_id
        ).all()

    #  Others → not allowed
    raise HTTPException(status_code=403, detail="Not authorized")

@router.get("/get-categories")
def get_categories(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # optional: remove this if all users can access
    if current_user.role_id not in [ADMIN, ANALYST, USER]:
        raise HTTPException(status_code=403, detail="Not authorized")

    categories = db.query(Category).all()

    return [
        {
            "id": c.id,
            "name": c.name
        }
        for c in categories
    ]

@router.patch("/{user_id}")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    #  Only Admin
    if current_user.role_id != ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    #   Update role
    if user_update.role_id is not None:
        user.role_id = user_update.role_id

    #   Update department
    if user_update.department_id is not None:
        user.department_id = user_update.department_id

    #   Activate / deactivate
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)

    return {
        "message": "User updated successfully",
        "user_id": user.id,
        "role_id": user.role_id,
        "department_id": user.department_id,
        "is_active": user.is_active
    }

@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return current_user