from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Record
from models.user import User
from schemas.record import RecordCreate
from utils.dependencies import get_current_user
from utils.roles import ADMIN, ANALYST, Viewer as USER
from models import Category
from datetime import datetime


router = APIRouter(prefix="/records", tags=["Records"])


# -----------------------------
# CREATE RECORD (Admin only)
# -----------------------------

@router.post("/")
def create_record(
    record: RecordCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role_id in [USER, ANALYST]:
        raise HTTPException(status_code=403, detail="Viewer or Analyst cannot create records")

    if record.amount is None or record.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    if record.type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Type must be 'income' or 'expense'")

    if not record.category_id and not record.custom_category:
        raise HTTPException(status_code=400, detail="Provide category_id or custom_category")

    if record.category_id and record.custom_category:
        raise HTTPException(status_code=400, detail="Choose either category_id or custom_category")

    if not record.description or len(record.description.strip()) == 0:
        raise HTTPException(status_code=400, detail="Description cannot be empty")

    if len(record.description) > 255:
        raise HTTPException(status_code=400, detail="Description too long (max 255 characters)")

    if record.category_id:
        category = db.query(Category).filter(Category.id == record.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    category_id = None if record.category_id == 0 else record.category_id
    db_record = Record(
        amount=record.amount,
        description=record.description.strip(),
        category_id=category_id,
        custom_category=record.custom_category,
        created_by=current_user.id,
        type=record.type,
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record


# -----------------------------
# VIEW OWN RECORDS (ALL USERS)
# -----------------------------

@router.get("/my")
def get_my_records(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Record).filter(
        Record.created_by == current_user.id
    ).all()


# -----------------------------
# ANALYST + ADMIN -- DEPARTMENT
# -----------------------------

@router.get("/department")
def get_department_records(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role_id not in [ANALYST, ADMIN]:
        raise HTTPException(status_code=403, detail="Analyst and Admin only")

    # -------------------------
    # ANALYST -- only own dept
    # -------------------------
    if current_user.role_id == ANALYST:
        records = db.query(Record)\
            .join(User, Record.created_by == User.id)\
            .filter(User.department_id == current_user.department_id)\
            .all()

        return records

    # -------------------------
    # ADMIN -- group by department
    # -------------------------
    records = db.query(Record, User.department_id)\
        .join(User, Record.created_by == User.id)\
        .all()

    result = {}

    for record, dept_id in records:
        dept_key = f"department_{dept_id}"

        if dept_key not in result:
            result[dept_key] = []

        result[dept_key].append(record)

    return result

# -----------------------------
# ADMIN -- ALL RECORDS
# -----------------------------

@router.get("/all")
def get_all_records(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role_id != ADMIN:
        raise HTTPException(403, "Admin only")

    return db.query(Record).all()


# -----------------------------
# DELETE RECORD (Admin only)
# -----------------------------

@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role_id != ADMIN:
        raise HTTPException(403, "Only admin can delete records")

    record = db.query(Record).filter(Record.id == record_id).first()

    if not record:
        raise HTTPException(404, "Record not found")

    db.delete(record)
    db.commit()

    return {"message": "Deleted successfully"}


# -----------------------------
# FILTER (ALL USERS)
# -----------------------------

@router.get("/filter")
def filter_records(
    type: str = None,
    category_id: int = None,
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Record)

    if current_user.role_id == USER:
        query = query.filter(Record.created_by == current_user.id)

    if type:
        query = query.filter(Record.type == type)

    if category_id:
        query = query.filter(Record.category_id == category_id)

    if start_date and end_date:
        query = query.filter(Record.created_at.between(start_date, end_date))

    return query.all()


# -----------------------------
# ADMIN -- APPROVE / REJECT
# -----------------------------

@router.patch("/{record_id}/status")
def update_status(
    record_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role_id != ADMIN:
        raise HTTPException(status_code=403, detail="Admin only authorized")

    allowed_status = ["pending", "approved", "rejected"]

    if status not in allowed_status:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {allowed_status}"
        )

    record = db.query(Record).filter(Record.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    record.status = status
    record.reviewed_by = current_user.id
    record.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(record)

    return {
        "message": "Status updated",
        "record_id": record.id,
        "status": record.status,
        "reviewed_by": record.reviewed_by,
        "reviewed_at": record.reviewed_at
    }

# -----------------------------
# UPDATE RECORD (Admin only)
# -----------------------------
@router.put("/{record_id}")
def update_record(
    record_id: int,
    updated_record: RecordCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role_id != ADMIN:
        raise HTTPException(403, "Only admin can update records")

    record = db.query(Record).filter(Record.id == record_id).first()

    if not record:
        raise HTTPException(404, "Record not found")

    if updated_record.amount is None or updated_record.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    if updated_record.type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Type must be 'income' or 'expense'")
    
    if not updated_record.description or len(updated_record.description.strip()) == 0:
        raise HTTPException(status_code=400, detail="Description cannot be empty")

    if len(updated_record.description) > 255:
        raise HTTPException(status_code=400, detail="Description too long (max 255 characters)")

    if not updated_record.category_id and not updated_record.custom_category:
        raise HTTPException(400, "Provide category_id or custom_category")

    if updated_record.category_id and updated_record.custom_category:
        raise HTTPException(400, "Choose either category_id or custom_category")

    if updated_record.category_id:
        category = db.query(Category).filter(Category.id == updated_record.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    category_id = None if updated_record.category_id == 0 else updated_record.category_id
    record.amount = updated_record.amount
    record.description = updated_record.description
    record.category_id = category_id
    record.custom_category = updated_record.custom_category
    record.type = updated_record.type

    db.commit()
    db.refresh(record)

    return {
        "message": "Record updated successfully",
        "record": record
    }