from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Record
from models.user import User   # IMPORTANT
from schemas.record import RecordCreate
from utils.dependencies import get_current_user

router = APIRouter(prefix="/records", tags=["Records"])


# -------------------------------
# CREATE RECORD
# -------------------------------
@router.post("/")
def create_record(
    record: RecordCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # ❌ both empty
    if not record.category_id and not record.custom_category:
        raise HTTPException(status_code=400, detail="Provide category_id or custom_category")

    # ❌ both given
    if record.category_id and record.custom_category:
        raise HTTPException(status_code=400, detail="Choose either category_id or custom_category, not both")

    # 🔁 convert 0 → None
    if record.category_id == 0:
        record.category_id = None

    db_record = Record(
        amount=record.amount,
        purpose=record.purpose,
        category_id=record.category_id,
        custom_category=record.custom_category,
        created_by=user.id
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record


# -------------------------------
#  USER → OWN RECORDS
# -------------------------------
@router.get("/my")
def get_my_records(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Record).filter(Record.created_by == user.id).all()


# -------------------------------
#  ANALYST → DEPARTMENT RECORDS
# -------------------------------
@router.get("/department")
def get_department_records(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="Not allowed")

    return db.query(Record).join(
        User, Record.created_by == User.id   # ✅ FIX HERE
    ).filter(
        User.department_id == user.department_id
    ).all()


# -------------------------------
#  ADMIN → ALL RECORDS
# -------------------------------
@router.get("/")
def get_all_records(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin only")

    return db.query(Record).all()


# -------------------------------
#  ADMIN → APPROVE / REJECT
# -------------------------------
@router.patch("/{record_id}/status")
def update_status(
    record_id: int,
    status: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin only")

    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    record = db.query(Record).filter(Record.id == record_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    record.status = status
    record.reviewed_by = user.id

    db.commit()
    db.refresh(record)

    return {
        "message": "Status updated",
        "record_id": record.id,
        "status": record.status
    }