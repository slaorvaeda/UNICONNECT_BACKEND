from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core import models, schemas
from typing import List
import datetime

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    student_count = db.query(models.User).filter(models.User.role == "student").count()
    teacher_count = db.query(models.User).filter(models.User.role == "teacher").count()
    pending_grievances = db.query(models.Grievance).filter(models.Grievance.status != "resolved").count()
    
    return {
        "student_count": student_count,
        "teacher_count": teacher_count,
        "pending_grievances_count": pending_grievances
    }

@router.get("/students", response_model=List[schemas.UserResponse])
def get_students(db: Session = Depends(get_db)):
    students = db.query(models.User).filter(models.User.role == "student").all()
    return students

@router.post("/students", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_student(request: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(models.User).filter(func.lower(models.User.email) == func.lower(request.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    
    new_student = models.User(
        name=request.name,
        email=request.email,
        role="student",
        student_id=request.student_id,
        department=request.department,
        year=request.year,
        section=request.section,
        dob=request.dob,
        phone=request.phone,
        gender=request.gender,
        blood_group=request.blood_group,
        address=request.address
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@router.get("/teachers", response_model=List[schemas.UserResponse])
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(models.User).filter(models.User.role == "teacher").all()
    return teachers

@router.post("/teachers", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(request: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(func.lower(models.User.email) == func.lower(request.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    
    new_teacher = models.User(
        name=request.name,
        email=request.email,
        role="teacher",
        department=request.department,
        employee_id=request.employee_id,
        designation=request.designation,
        dob=request.dob,
        phone=request.phone,
        gender=request.gender,
        blood_group=request.blood_group,
        address=request.address
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher

@router.post("/notices", response_model=schemas.NoticeResponse, status_code=status.HTTP_201_CREATED)
def create_notice(request: schemas.NoticeCreate, db: Session = Depends(get_db)):
    new_notice = models.Notice(
        title=request.title,
        body=request.body,
        date=request.date,
        category=request.category
    )
    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)
    return new_notice

@router.post("/events", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(request: schemas.EventCreate, db: Session = Depends(get_db)):
    new_event = models.Event(
        title=request.title,
        description=request.description,
        date=request.date,
        type=request.type,
        venue=request.venue
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@router.get("/grievances", response_model=List[schemas.GrievanceResponse])
def get_grievances(db: Session = Depends(get_db)):
    grievances = db.query(models.Grievance).all()
    return grievances

class GrievanceResolveRequest(schemas.BaseModel):
    status: str
    response: str

@router.put("/grievances/{grievance_id}", response_model=schemas.GrievanceResponse)
def resolve_grievance(grievance_id: int, request: GrievanceResolveRequest, db: Session = Depends(get_db)):
    grievance = db.query(models.Grievance).filter(models.Grievance.id == grievance_id).first()
    if not grievance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grievance ticket not found."
        )
    
    grievance.status = request.status
    grievance.response = request.response
    grievance.updated_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(grievance)
    return grievance

@router.delete("/notices/{notice_id}", status_code=status.HTTP_200_OK)
def delete_notice(notice_id: int, db: Session = Depends(get_db)):
    notice = db.query(models.Notice).filter(models.Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found.")
    db.delete(notice)
    db.commit()
    return {"message": "Notice deleted successfully"}

@router.delete("/events/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}

@router.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.User).filter(models.User.id == student_id, models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}

@router.delete("/teachers/{teacher_id}", status_code=status.HTTP_200_OK)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.User).filter(models.User.id == teacher_id, models.User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")
    db.delete(teacher)
    db.commit()
    return {"message": "Teacher deleted successfully"}

class FeeCreateRequest(schemas.BaseModel):
    student_email: str
    amount: float
    due_date: str # YYYY-MM-DD

@router.get("/fees")
def get_all_fees(db: Session = Depends(get_db)):
    records = db.query(models.FeeRecord).all()
    result = []
    for r in records:
        student = db.query(models.User).filter(models.User.id == r.student_id).first()
        result.append({
            "id": r.id,
            "student_name": student.name if student else "Unknown",
            "student_email": student.email if student else "Unknown",
            "amount": r.amount,
            "status": r.status,
            "due_date": str(r.due_date),
            "paid_at": str(r.paid_at) if r.paid_at else None
        })
    return result

@router.post("/fees")
def create_fee(request: FeeCreateRequest, db: Session = Depends(get_db)):
    student = db.query(models.User).filter(func.lower(models.User.email) == func.lower(request.student_email), models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student with this email not found.")
        
    try:
        due = datetime.datetime.strptime(request.due_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Date format must be YYYY-MM-DD.")
        
    new_fee = models.FeeRecord(
        student_id=student.id,
        amount=request.amount,
        due_date=due,
        status="pending"
    )
    db.add(new_fee)
    db.commit()
    db.refresh(new_fee)
    return {"message": "Fee record created successfully", "id": new_fee.id}

@router.delete("/fees/{fee_id}")
def delete_fee(fee_id: int, db: Session = Depends(get_db)):
    fee = db.query(models.FeeRecord).filter(models.FeeRecord.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found.")
    db.delete(fee)
    db.commit()
    return {"message": "Fee record deleted successfully"}

# Department endpoints
@router.get("/departments", response_model=List[schemas.DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).all()

@router.post("/departments", response_model=schemas.DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(request: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Department).filter(func.lower(models.Department.name) == func.lower(request.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department with this name already exists.")
    new_dept = models.Department(name=request.name, code=request.code)
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept

@router.delete("/departments/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found.")
    db.delete(dept)
    db.commit()
    return {"message": "Department deleted successfully"}

# Timetable endpoints
@router.get("/timetable", response_model=List[schemas.TimetableSlotResponse])
def get_admin_timetable(db: Session = Depends(get_db)):
    return db.query(models.TimetableSlot).all()

@router.post("/timetable", response_model=schemas.TimetableSlotResponse, status_code=status.HTTP_201_CREATED)
def create_timetable_slot(request: schemas.TimetableSlotCreate, db: Session = Depends(get_db)):
    new_slot = models.TimetableSlot(
        department=request.department,
        year=request.year,
        section=request.section,
        day=request.day,
        subject=request.subject,
        time_slot=request.time_slot,
        room=request.room,
        scheme=request.scheme,
        semester=request.semester,
        teacher_name=request.teacher_name
    )
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    return new_slot

@router.delete("/timetable/{slot_id}")
def delete_timetable_slot(slot_id: int, db: Session = Depends(get_db)):
    slot = db.query(models.TimetableSlot).filter(models.TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Timetable slot not found.")
    db.delete(slot)
    db.commit()
    return {"message": "Timetable slot deleted successfully"}

# Subject endpoints
@router.get("/subjects", response_model=List[schemas.SubjectResponse])
def get_admin_subjects(db: Session = Depends(get_db)):
    return db.query(models.Subject).all()

@router.post("/subjects", response_model=schemas.SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(request: schemas.SubjectCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Subject).filter(models.Subject.name == request.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject with this name already registered.")
    
    new_sub = models.Subject(
        name=request.name,
        code=request.code
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub

@router.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    sub = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found.")
    db.delete(sub)
    db.commit()
    return {"message": "Subject deleted successfully"}
