from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecordCreate(BaseModel):
    amount: float
    description: str
    category_id: Optional[int] = None
    custom_category: Optional[str] = None
    type: str  # income / expense

class RecordResponse(BaseModel):
    id: int
    amount: float
    purpose: str
    status: str

    class Config:
        from_attributes = True