from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from pydantic import BaseModel
from app.core import models, schemas
from app.core.database import get_db

router = APIRouter()

class AttendanceBatchCreate(BaseModel):
    date: str  # YYYY-MM-DD
    records: Dict[int, str]  # student_id -> "present" / "absent"

class GrievanceResolve(BaseModel):
    status: str
    response: str

@router.get("/students", response_model=List[schemas.UserResponse])
def get_students(
    department: str = None,
    year: str = None,
    section: str = None,
    db: Session = Depends(get_db)
):
    # Returns filtered students for attendance marking
    query = db.query(models.User).filter(models.User.role == "student")
    if department:
        query = query.filter(models.User.department == department)
    if year:
        query = query.filter(models.User.year == year)
    if section:
        query = query.filter(models.User.section == section)
    return query.all()

@router.post("/attendance", status_code=status.HTTP_200_OK)
def log_attendance(request: AttendanceBatchCreate, db: Session = Depends(get_db)):
    import datetime
    try:
        date_obj = datetime.date.fromisoformat(request.date)
    except ValueError:
        date_obj = datetime.date.today()

    for student_id, status_val in request.records.items():
        # Validate student exists
        student = db.query(models.User).filter(models.User.id == student_id, models.User.role == "student").first()
        if not student:
            continue
            
        # Check if record already exists for this student and date
        existing = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.student_id == student_id,
            models.AttendanceRecord.date == date_obj
        ).first()
        
        if existing:
            existing.status = status_val
        else:
            new_record = models.AttendanceRecord(
                student_id=student_id,
                date=date_obj,
                status=status_val
            )
            db.add(new_record)
            
    db.commit()
    return {"message": "Attendance logs updated successfully"}

@router.get("/grievances", response_model=List[schemas.GrievanceResponse])
def get_grievances(db: Session = Depends(get_db)):
    grievances = db.query(models.Grievance).order_by(models.Grievance.created_at.desc()).all()
    return grievances

@router.put("/grievances/{grievance_id}", response_model=schemas.GrievanceResponse)
def resolve_grievance(grievance_id: int, request: GrievanceResolve, db: Session = Depends(get_db)):
    grievance = db.query(models.Grievance).filter(models.Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found.")
        
    grievance.status = request.status
    grievance.response = request.response
    db.commit()
    db.refresh(grievance)
    return grievance

class GradeCreateRequest(BaseModel):
    student_id: int
    subject: str
    semester: str
    marks: float
    max_marks: float
    grade: str

@router.post("/grades", status_code=status.HTTP_201_CREATED)
def create_grade(request: GradeCreateRequest, db: Session = Depends(get_db)):
    student = db.query(models.User).filter(models.User.id == request.student_id, models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
        
    new_grade = models.AcademicRecord(
        student_id=request.student_id,
        subject=request.subject,
        semester=request.semester,
        marks=request.marks,
        max_marks=request.max_marks,
        grade=request.grade
    )
    db.add(new_grade)
    db.commit()
    db.refresh(new_grade)
    return {"message": "Academic grade log saved successfully", "id": new_grade.id}

@router.get("/departments", response_model=List[schemas.DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).all()

@router.get("/timetable", response_model=List[schemas.TimetableSlotResponse])
def get_teacher_timetable(
    department: str = None,
    year: str = None,
    section: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.TimetableSlot)
    if department:
        query = query.filter(models.TimetableSlot.department == department)
    if year:
        query = query.filter(models.TimetableSlot.year == year)
    if section:
        query = query.filter(models.TimetableSlot.section == section)
    return query.all()

@router.get("/subjects", response_model=List[schemas.SubjectResponse])
def get_teacher_subjects(db: Session = Depends(get_db)):
    return db.query(models.Subject).all()

@router.post("/materials", response_model=schemas.StudyMaterialResponse, status_code=status.HTTP_201_CREATED)
def create_study_material(request: schemas.StudyMaterialCreate, db: Session = Depends(get_db)):
    new_material = models.StudyMaterial(
        title=request.title,
        description=request.description,
        file_url=request.file_url,
        subject=request.subject,
        teacher_name=request.teacher_name,
        department=request.department,
        scheme=request.scheme,
        year=request.year,
        semester=request.semester
    )
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    return new_material

@router.get("/materials", response_model=List[schemas.StudyMaterialResponse])
def get_study_materials(teacher_name: str = None, db: Session = Depends(get_db)):
    query = db.query(models.StudyMaterial)
    if teacher_name:
        query = query.filter(models.StudyMaterial.teacher_name == teacher_name)
    return query.order_by(models.StudyMaterial.created_at.desc()).all()

@router.delete("/materials/{material_id}", status_code=status.HTTP_200_OK)
def delete_study_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(models.StudyMaterial).filter(models.StudyMaterial.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Study material not found.")
    db.delete(material)
    db.commit()
    return {"message": "Study material deleted successfully"}
