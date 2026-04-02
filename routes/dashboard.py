from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from database import get_db
from models import Record, User, Category
from utils.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/total-expense")
def total_expense(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = db.query(func.sum(Record.amount))

    # Admin → all data
    if user.role_id == 1:
        total = query.scalar()

    # Analyst → department data
    elif user.role_id == 2:
        total = query.join(User, Record.created_by == User.id)\
                     .filter(User.department_id == user.department_id)\
                     .scalar()

    # User → own data
    else:
        total = query.filter(Record.created_by == user.id).scalar()

    return {"total_expense": total or 0}

@router.get("/category-wise")
def category_wise(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = db.query(
        Category.name,
        func.sum(Record.amount)
    ).join(Category, Record.category_id == Category.id)

    if user.role_id == 1:
        data = query.group_by(Category.name).all()

    elif user.role_id == 2:
        data = query.join(User, Record.created_by == User.id)\
                    .filter(User.department_id == user.department_id)\
                    .group_by(Category.name).all()

    else:
        data = query.filter(Record.created_by == user.id)\
                    .group_by(Category.name).all()

    return [{"category": d[0], "total": d[1]} for d in data]

@router.get("/monthly")
def monthly_trends(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = db.query(
        func.to_char(Record.created_at, 'YYYY-MM'),
        func.sum(Record.amount)
    )

    if user.role_id == 1:
        data = query.group_by(func.to_char(Record.created_at, 'YYYY-MM')).all()

    elif user.role_id == 2:
        data = query.join(User, Record.created_by == User.id)\
                    .filter(User.department_id == user.department_id)\
                    .group_by(func.to_char(Record.created_at, 'YYYY-MM')).all()

    else:
        data = query.filter(Record.created_by == user.id)\
                    .group_by(func.to_char(Record.created_at, 'YYYY-MM')).all()

    return [{"month": d[0], "total": d[1]} for d in data]

@router.get("/recent")
def recent_activity(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = db.query(Record).order_by(Record.created_at.desc())

    if user.role_id == 1:
        data = query.limit(5).all()

    elif user.role_id == 2:
        data = query.join(User, Record.created_by == User.id)\
                    .filter(User.department_id == user.department_id)\
                    .limit(5).all()

    else:
        data = query.filter(Record.created_by == user.id)\
                    .limit(5).all()

    return data