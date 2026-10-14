from pydantic import BaseModel
from typing import Optional, List
import datetime

# User Schemas
class UserBase(BaseModel):
    name: str
    email: str
    role: Optional[str] = "student"
    student_id: Optional[str] = None
    employee_id: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    section: Optional[str] = None
    dob: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    role: Optional[str] = None

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


# Attendance Schemas
class AttendanceBase(BaseModel):
    subject: str
    date: datetime.date
    status: str
    percentage: float

class AttendanceResponse(AttendanceBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True


# Event Schemas
class EventBase(BaseModel):
    title: str
    description: str
    date: datetime.date
    type: str
    venue: str

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

    class Config:
        from_attributes = True


# Grievance Schemas
class GrievanceBase(BaseModel):
    subject: str
    description: str

class GrievanceCreate(GrievanceBase):
    pass

class GrievanceResponse(GrievanceBase):
    id: int
    student_id: int
    status: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    response: Optional[str] = None

    class Config:
        from_attributes = True


# Notice Schemas
class NoticeBase(BaseModel):
    title: str
    body: str
    date: datetime.date
    category: str

class NoticeCreate(NoticeBase):
    pass

class NoticeResponse(NoticeBase):
    id: int

    class Config:
        from_attributes = True


# Fee Schemas
class FeeBase(BaseModel):
    amount: float
    due_date: datetime.date
    status: str

class FeeResponse(FeeBase):
    id: int
    student_id: int
    paid_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


# Academic Records Schemas
class AcademicRecordBase(BaseModel):
    subject: str
    semester: str
    marks: int
    max_marks: int
    grade: str

class AcademicRecordResponse(AcademicRecordBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True


# Exam Schedule Schemas
class ExamScheduleResponse(BaseModel):
    id: int
    subject: str
    date: datetime.date
    time: str
    venue: str

    class Config:
        from_attributes = True

class ChatMessageSchema(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessageSchema]
    student_id: Optional[int] = None

# Department Schemas
class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


# Timetable Schemas
class TimetableSlotBase(BaseModel):
    department: str
    year: str
    section: str
    day: str
    subject: str
    time_slot: str
    room: Optional[str] = None
    scheme: Optional[str] = "yearly"
    semester: Optional[str] = None
    teacher_name: Optional[str] = None

class TimetableSlotCreate(TimetableSlotBase):
    pass

class TimetableSlotResponse(TimetableSlotBase):
    id: int

    class Config:
        from_attributes = True


# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True

# Study Material Schemas
class StudyMaterialBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_url: str
    subject: str
    teacher_name: str
    department: str
    scheme: str = "yearly"
    year: Optional[str] = None
    semester: Optional[str] = None

class StudyMaterialCreate(StudyMaterialBase):
    pass

class StudyMaterialResponse(StudyMaterialBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True
