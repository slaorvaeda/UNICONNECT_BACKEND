from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import models, schemas

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(schemas.BaseModel):
    email: str
    password: str

@router.post("/login", response_model=schemas.UserResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Basic lookup by email (ignoring password encryption for local demo purposes)
    user = db.query(models.User).filter(func.lower(models.User.email) == func.lower(request.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this email."
        )
    # Match frontend's dummy password logic
    if request.password != "123456":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )
    return user
