from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Record
from models.user import User
from schemas.record import RecordCreate
from utils.dependencies import get_current_user

# -----------------------------------
# ROLE DEFINITIONS
# -----------------------------------
from utils.roles import ADMIN, ANALYST, USER


router = APIRouter(prefix="/records", tags=["Records"])

# -----------------------------------
# CREATE RECORD (ALL LOGGED USERS)
# -----------------------------------
@router.post("/")
def create_record(
    record: RecordCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    #  both empty
    if not record.category_id and not record.custom_category:
        raise HTTPException(status_code=400, detail="Provide category_id or custom_category")

    #  both given
    if record.category_id and record.custom_category:
        raise HTTPException(status_code=400, detail="Choose either category_id or custom_category")

    #  convert 0 → None
    category_id = None if record.category_id == 0 else record.category_id

    db_record = Record(
        amount=record.amount,
        purpose=record.purpose,
        category_id=category_id,
        custom_category=record.custom_category,
        created_by=current_user.id,
        approval_deadline=record.approval_date,
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record


# -----------------------------------
# USER → OWN RECORDS
# -----------------------------------
@router.get("/my")
def get_my_records(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Record).filter(
        Record.created_by == current_user.id
    ).all()


# -----------------------------------
# ANALYST → DEPARTMENT RECORDS ONLY
# -----------------------------------
@router.get("/department")
def get_department_records(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role_id != ANALYST and current_user.role_id != ADMIN:
        raise HTTPException(status_code=403, detail="Analyst and Admin only")

    return db.query(Record).join(
        User, Record.created_by == User.id
    ).filter(
        User.department_id == current_user.department_id
    ).all()


# -----------------------------------
# ADMIN → ALL RECORDS
# -----------------------------------
@router.get("/all")
def get_all_records(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role_id != ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")

    return db.query(Record).all()


# -----------------------------------
# ADMIN → APPROVE / REJECT
# -----------------------------------
@router.patch("/{record_id}/status")
def update_status(
    record_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role_id != ADMIN:
        raise HTTPException(status_code=403, detail="Admin only")

    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    record = db.query(Record).filter(Record.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    record.status = status
    record.reviewed_by = current_user.id

    db.commit()
    db.refresh(record)

    return {
        "message": "Status updated",
        "record_id": record.id,
        "status": record.status
    }

@router.put("/{record_id}")
def update_record(
    record_id: int,
    updated_record: RecordCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    record = db.query(Record).filter(Record.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Only owner OR admin can edit
    if record.created_by != current_user.id and current_user.role_id != ADMIN:
        raise HTTPException(status_code=403, detail="Not allowed to edit this record")

    # both empty
    if not updated_record.category_id and not updated_record.custom_category:
        raise HTTPException(status_code=400, detail="Provide category_id or custom_category")

    # both given
    if updated_record.category_id and updated_record.custom_category:
        raise HTTPException(status_code=400, detail="Choose either category_id or custom_category")

    # convert 0 → None
    category_id = None if updated_record.category_id == 0 else updated_record.category_id

    # update fields
    record.amount = updated_record.amount
    record.purpose = updated_record.purpose
    record.category_id = category_id
    record.custom_category = updated_record.custom_category
    record.approval_deadline = updated_record.approval_date

    db.commit()
    db.refresh(record)

    return {
        "message": "Record updated successfully",
        "record": record
    }