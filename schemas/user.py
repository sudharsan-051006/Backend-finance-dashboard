from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes  = True

from pydantic import BaseModel
from typing import Optional

class UserUpdate(BaseModel):
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None