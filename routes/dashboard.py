from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from database import get_db
from models import Record, User, Category
from utils.dependencies import get_current_user

from utils.roles import ADMIN, ANALYST, Viewer as USER


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
@router.get("/total-expense")
def total_expense(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    base_filter = [
        Record.type == "expense",
        Record.status == "approved"
    ]

    # -------------------------
    # USER --- own expense
    # -------------------------
    user_total = db.query(func.sum(Record.amount)).filter(
        Record.created_by == user.id,
        *base_filter
    ).scalar() or 0

    response = {
        "user_total_expense": user_total
    }

    # -------------------------
    # ANALYST --- department total
    # -------------------------
    if user.role_id == ANALYST:
        dept_total = db.query(func.sum(Record.amount))\
            .join(User, Record.created_by == User.id)\
            .filter(
                User.department_id == user.department_id,
                *base_filter
            ).scalar() or 0

        response["department_total_expense"] = dept_total

    # -------------------------
    # ADMIN --- global total
    # -------------------------
    elif user.role_id == ADMIN:
        global_total = db.query(func.sum(Record.amount)).filter(
            *base_filter
        ).scalar() or 0

        response["global_total_expense"] = global_total

    return response

@router.get("/total")
def net_balance_and_income(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    base_filter = [Record.status == "approved"]

    # -------------------------
    # USER (always include)
    # -------------------------
    user_income = db.query(func.sum(Record.amount)).filter(
        Record.type == "income",
        Record.created_by == user.id,
        *base_filter
    ).scalar() or 0

    user_expense = db.query(func.sum(Record.amount)).filter(
        Record.type == "expense",
        Record.created_by == user.id,
        *base_filter
    ).scalar() or 0

    response = {
        "user": {
            "income": user_income,
            "expense": user_expense,
            "net_balance": user_income - user_expense
        }
    }

    # -------------------------
    # ANALYST → department
    # -------------------------
    if user.role_id == ANALYST:
        dept_income = db.query(func.sum(Record.amount))\
            .join(User, Record.created_by == User.id)\
            .filter(
                Record.type == "income",
                User.department_id == user.department_id,
                *base_filter
            ).scalar() or 0

        dept_expense = db.query(func.sum(Record.amount))\
            .join(User, Record.created_by == User.id)\
            .filter(
                Record.type == "expense",
                User.department_id == user.department_id,
                *base_filter
            ).scalar() or 0

        response["department"] = {
            "income": dept_income,
            "expense": dept_expense,
            "net_balance": dept_income - dept_expense
        }

    # -------------------------
    # ADMIN → global
    # -------------------------
    elif user.role_id == ADMIN:
        global_income = db.query(func.sum(Record.amount)).filter(
            Record.type == "income",
            *base_filter
        ).scalar() or 0

        global_expense = db.query(func.sum(Record.amount)).filter(
            Record.type == "expense",
            *base_filter
        ).scalar() or 0

        response["global"] = {
            "income": global_income,
            "expense": global_expense,
            "net_balance": global_income - global_expense
        }

    return response

@router.get("/category-wise")
def category_wise(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = db.query(
        func.coalesce(Category.name, "Other").label("category"),
        func.sum(Record.amount).label("total")
    ).outerjoin(Category, Record.category_id == Category.id)

    if user.role_id == ADMIN:
        data = query.group_by("category").all()

    elif user.role_id == ANALYST:
        data = query.join(User, Record.created_by == User.id)\
                    .filter(User.department_id == user.department_id)\
                    .group_by("category").all()

    else:
        data = query.filter(Record.created_by == user.id)\
                    .group_by("category").all()

    return [{"category": d.category, "total": d.total} for d in data]

@router.get("/monthly")
def monthly_trends(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    query = db.query(
        func.to_char(Record.created_at, 'YYYY-MM'),
        func.sum(Record.amount)
    )

    if user.role_id == ADMIN:
        data = query.group_by(func.to_char(Record.created_at, 'YYYY-MM')).all()

    elif user.role_id == ANALYST:
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

    if user.role_id == ADMIN:
        data = query.limit(5).all()

    elif user.role_id == ANALYST:
        data = query.join(User, Record.created_by == User.id)\
                    .filter(User.department_id == user.department_id)\
                    .limit(5).all()

    else:
        data = query.filter(Record.created_by == user.id)\
                    .limit(5).all()

    return data

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    def get_data(filter_query):
        data = db.query(
            Record.status,
            Record.type,
            func.sum(Record.amount).label("total")
        ).filter(*filter_query)\
         .group_by(Record.status, Record.type)\
         .all()

        result = {
            "approved": {"income": 0, "expense": 0},
            "pending": {"income": 0, "expense": 0},
            "rejected": {"income": 0, "expense": 0}
        }

        for status, type_, total in data:
            if status in result and type_ in ["income", "expense"]:
                result[status][type_] = float(total or 0)

        for status in result:
            result[status]["net_balance"] = (
                result[status]["income"] - result[status]["expense"]
            )

        return result

    # -------------------------
    # USER (always include)
    # -------------------------
    user_data = get_data([
        Record.created_by == user.id
    ])

    response = {
        "user": user_data
    }

    # -------------------------
    # ANALYST --- department
    # -------------------------
    if user.role_id == ANALYST:
        dept_data = get_data([
            Record.created_by == User.id,
            User.department_id == user.department_id
        ])

        # IMPORTANT: need join
        dept_data = db.query(
            Record.status,
            Record.type,
            func.sum(Record.amount)
        ).join(User, Record.created_by == User.id)\
         .filter(User.department_id == user.department_id)\
         .group_by(Record.status, Record.type)\
         .all()

        # reuse builder
        dept_result = {
            "approved": {"income": 0, "expense": 0},
            "pending": {"income": 0, "expense": 0},
            "rejected": {"income": 0, "expense": 0}
        }

        for status, type_, total in dept_data:
            if status in dept_result and type_ in ["income", "expense"]:
                dept_result[status][type_] = float(total or 0)

        for status in dept_result:
            dept_result[status]["net_balance"] = (
                dept_result[status]["income"] - dept_result[status]["expense"]
            )

        response["department"] = dept_result

    # -------------------------
    # ADMIN --- global
    # -------------------------
    elif user.role_id == ADMIN:
        global_data = get_data([])

        response["global"] = global_data

    return response