from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database import get_db
from models import User
from utils.jwt import SECRET_KEY, ALGORITHM

# 🔐 OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# 👤 Get current user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def require_role(allowed_roles: list):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role_id not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return role_checker