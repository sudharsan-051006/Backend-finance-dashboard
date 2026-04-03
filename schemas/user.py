from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int
    department_id: int


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes  = True

class UserUpdate(BaseModel):
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None