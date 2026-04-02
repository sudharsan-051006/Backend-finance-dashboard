from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Category
from schemas.user import UserCreate, UserUpdate
from utils.dependencies import get_current_user, require_role

router = APIRouter(prefix="/users")

@router.post("/")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)   # add this
):
    # Restrict access
    if current_user.id != 3:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_user = User(
        name=user.name,
        email=user.email,
        password=user.password,
        role_id=user.role_id,
        department_id=user.department_id,
        emp_id="EMP"  # temporary
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
    #   Admin only
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Not authorized")

    users = db.query(User).all()

    return users

@router.get("/get-categories")
def get_categories(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # optional: remove this if all users can access
    if current_user.role_id not in [1, 2, 3]:
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
    #   Only Admin
    if current_user.role_id != 1:
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

@router.get("/admin-only")
def admin_only(user = Depends(require_role([1]))):
    return {"message": "Admin access"}

@router.get("/analytics")
def analytics(user = Depends(require_role([1, 2]))):
    return {"message": "Analytics access"}