from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)  # student, teacher, admin
    student_id = Column(String, unique=True, index=True, nullable=True) # e.g. 1AR23IS003
    employee_id = Column(String, unique=True, index=True, nullable=True) # e.g. EMP001
    designation = Column(String, nullable=True) # e.g. Assistant Professor
    department = Column(String, nullable=True)
    year = Column(String, nullable=True)
    section = Column(String, nullable=True)
    dob = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    address = Column(String, nullable=True)

    # Relationships
    attendance = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")
    grievances = relationship("Grievance", back_populates="student", cascade="all, delete-orphan")
    fees = relationship("FeeRecord", back_populates="student", cascade="all, delete-orphan")
    academic_records = relationship("AcademicRecord", back_populates="student", cascade="all, delete-orphan")


class AttendanceRecord(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String, nullable=True)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False) # present, absent
    percentage = Column(Float, nullable=True)

    student = relationship("User", back_populates="attendance")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False) # event, sports, cultural
    venue = Column(String, nullable=False)


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="pending") # pending, in_progress, resolved
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.datetime.utcnow)
    response = Column(Text, nullable=True)

    student = relationship("User", back_populates="grievances")


class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    category = Column(String, nullable=False) # Academics, Administration, etc.


class FeeRecord(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, default="pending") # pending, paid
    paid_at = Column(DateTime, nullable=True)

    student = relationship("User", back_populates="fees")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, nullable=True)


class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    marks = Column(Integer, nullable=False)
    max_marks = Column(Integer, nullable=False)
    grade = Column(String, nullable=False)

    student = relationship("User", back_populates="academic_records")


class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(String, nullable=False)
    venue = Column(String, nullable=False)


class TimetableSlot(Base):
    __tablename__ = "timetable_slots"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, nullable=False)
    year = Column(String, nullable=False)
    section = Column(String, nullable=False)
    day = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    time_slot = Column(String, nullable=False)
    room = Column(String, nullable=True)
    scheme = Column(String, nullable=False, default="yearly")
    semester = Column(String, nullable=True)
    teacher_name = Column(String, nullable=True)

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String, nullable=True)

class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    teacher_name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    scheme = Column(String, nullable=False, default="yearly")
    year = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
