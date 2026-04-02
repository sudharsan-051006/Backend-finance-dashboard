from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecordCreate(BaseModel):
    amount: float
    purpose: str
    category_id: Optional[int] = None
    custom_category: Optional[str] = None
    approval_date: Optional[datetime] = None   # added

class RecordResponse(BaseModel):
    id: int
    amount: float
    purpose: str
    status: str

    class Config:
        from_attributes = True