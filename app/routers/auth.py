from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import models, schemas

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(schemas.BaseModel):
    email: str
    password: str

def compute_dob_passwords(dob_str: str) -> list:
    """Extract valid password formats from Date of Birth string (e.g. '08.09.2005' -> '08092005')."""
    if not dob_str:
        return []
    cleaned = str(dob_str).replace(".", "").replace("-", "").replace("/", "").replace(" ", "").strip()
    passwords = [cleaned]
    
    # Handle YYYY-MM-DD -> DDMMYYYY
    if "-" in str(dob_str):
        parts = str(dob_str).split("-")
        if len(parts) == 3 and len(parts[0]) == 4:
            passwords.append(f"{parts[2]}{parts[1]}{parts[0]}")
    # Handle DD.MM.YYYY -> DDMMYYYY
    elif "." in str(dob_str):
        parts = str(dob_str).split(".")
        if len(parts) == 3 and len(parts[0]) <= 2 and len(parts[2]) == 4:
            passwords.append(f"{parts[0].zfill(2)}{parts[1].zfill(2)}{parts[2]}")
            
    return list(set(passwords))

@router.post("/login", response_model=schemas.UserResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    query_id = request.email.strip()
    
    # Lookup by Email OR Student ID / USN OR Phone
    user = db.query(models.User).filter(func.lower(models.User.email) == func.lower(query_id)).first()
    if not user:
        user = db.query(models.User).filter(
            (func.lower(models.User.student_id) == func.lower(query_id)) |
            (models.User.phone == query_id)
        ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this email, USN, or phone number."
        )

    # Validate Password: DOB (DDMMYYYY format) or master default '123456'
    valid_passwords = compute_dob_passwords(user.dob) + ["123456"]
    req_pwd = request.password.strip()

    if req_pwd not in valid_passwords:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please enter your Date of Birth as DDMMYYYY (e.g. 08092005)."
        )

    return user
