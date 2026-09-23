from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import models, schemas
from typing import List
import datetime

router = APIRouter(prefix="/api/student", tags=["student"])

@router.get("/{student_id}/attendance")
def get_attendance(student_id: int, db: Session = Depends(get_db)):
    records = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.student_id == student_id).all()
    return records

@router.get("/{student_id}/fees")
def get_fees(student_id: int, db: Session = Depends(get_db)):
    records = db.query(models.FeeRecord).filter(models.FeeRecord.student_id == student_id).all()
    return records

@router.post("/{student_id}/fees/{fee_id}/pay")
def pay_fee(student_id: int, fee_id: int, db: Session = Depends(get_db)):
    fee = db.query(models.FeeRecord).filter(
        models.FeeRecord.id == fee_id, 
        models.FeeRecord.student_id == student_id
    ).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found.")
    
    if fee.status == "paid":
         return {"message": "Fee already paid."}
         
    fee.status = "paid"
    fee.paid_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(fee)
    return {"message": "Payment successful."}

@router.get("/{student_id}/academic-records")
def get_academic_records(student_id: int, db: Session = Depends(get_db)):
    records = db.query(models.AcademicRecord).filter(models.AcademicRecord.student_id == student_id).all()
    return records

@router.get("/{student_id}/grievances")
def get_grievances(student_id: int, db: Session = Depends(get_db)):
    records = db.query(models.Grievance).filter(models.Grievance.student_id == student_id).order_by(models.Grievance.created_at.desc()).all()
    return records

class GrievanceCreate(schemas.BaseModel):
    subject: str
    description: str

@router.post("/{student_id}/grievances")
def create_grievance(student_id: int, request: GrievanceCreate, db: Session = Depends(get_db)):
    student = db.query(models.User).filter(models.User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
        
    db_grievance = models.Grievance(
        student_id=student_id,
        subject=request.subject,
        description=request.description,
        status="pending"
    )
    db.add(db_grievance)
    db.commit()
    db.refresh(db_grievance)
    return db_grievance

@router.get("/events")
def get_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).order_by(models.Event.date.asc()).all()
    return events

@router.get("/notices")
def get_notices(db: Session = Depends(get_db)):
    notices = db.query(models.Notice).order_by(models.Notice.date.desc()).all()
    return notices

@router.get("/exams")
def get_exams(db: Session = Depends(get_db)):
    exams = db.query(models.ExamSchedule).order_by(models.ExamSchedule.date.asc()).all()
    return exams

@router.get("/{student_id}/timetable", response_model=List[schemas.TimetableSlotResponse])
def get_student_timetable(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.User).filter(models.User.id == student_id, models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    slots = db.query(models.TimetableSlot).filter(
        models.TimetableSlot.department == student.department,
        models.TimetableSlot.year == student.year,
        models.TimetableSlot.section == student.section
    ).all()
    return slots

@router.get("/{student_id}/materials", response_model=List[schemas.StudyMaterialResponse])
def get_student_materials(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.User).filter(models.User.id == student_id, models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    materials = db.query(models.StudyMaterial).filter(
        models.StudyMaterial.department == student.department
    ).order_by(models.StudyMaterial.created_at.desc()).all()
    return materials
