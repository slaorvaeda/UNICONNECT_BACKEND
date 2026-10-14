import datetime
from sqlalchemy import func
from app.core import models
from app.core.database import engine, SessionLocal, Base
from app.students_data import STUDENTS_LIST

def seed_students(db):
    """Seed or update all 58 students from STUDENTS_LIST and generate baseline records."""
    print(f"Checking and synchronizing {len(STUDENTS_LIST)} students from dataset...")
    count_new = 0
    count_updated = 0
    
    for s in STUDENTS_LIST:
        user = db.query(models.User).filter(
            (func.lower(models.User.email) == s["email"].lower()) |
            (func.lower(models.User.student_id) == s["student_id"].lower())
        ).first()

        if not user:
            user = models.User(
                name=s["name"],
                email=s["email"],
                role="student",
                student_id=s["student_id"],
                department=s.get("department", "Information Science"),
                year=s.get("year", "3rd"),
                section=s.get("section", "A"),
                dob=s.get("dob"),
                phone=s.get("phone"),
                gender=s.get("gender", "Female"),
                blood_group="O+",
                address=s.get("address")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            count_new += 1
        else:
            user.name = s["name"]
            user.dob = s["dob"]
            user.phone = s["phone"]
            user.address = s["address"]
            user.gender = s["gender"]
            user.department = s.get("department", "Information Science")
            user.year = s.get("year", "3rd")
            user.section = s.get("section", "A")
            db.commit()
            count_updated += 1

        # 1. Baseline Attendance Records
        if db.query(models.AttendanceRecord).filter(models.AttendanceRecord.student_id == user.id).count() == 0:
            sample_att = [
                models.AttendanceRecord(student_id=user.id, subject="Database Management Systems", date=datetime.date(2025, 3, 10), status="present", percentage=91.5),
                models.AttendanceRecord(student_id=user.id, subject="Machine Learning", date=datetime.date(2025, 3, 9), status="present", percentage=88.0),
                models.AttendanceRecord(student_id=user.id, subject="Web Technology & Applications", date=datetime.date(2025, 3, 8), status="present", percentage=85.0),
                models.AttendanceRecord(student_id=user.id, subject="Operating Systems", date=datetime.date(2025, 3, 7), status="present", percentage=93.0),
            ]
            db.add_all(sample_att)

        # 2. Baseline Fee Records
        if db.query(models.FeeRecord).filter(models.FeeRecord.student_id == user.id).count() == 0:
            sample_fees = [
                models.FeeRecord(student_id=user.id, amount=45000.0, due_date=datetime.date(2026, 11, 30), status="pending"),
                models.FeeRecord(student_id=user.id, amount=5000.0, due_date=datetime.date(2026, 8, 15), status="paid", paid_at=datetime.datetime(2026, 8, 10, 10, 30))
            ]
            db.add_all(sample_fees)

        # 3. Baseline Academic Records (Marks & Grades)
        if db.query(models.AcademicRecord).filter(models.AcademicRecord.student_id == user.id).count() == 0:
            sample_marks = [
                models.AcademicRecord(student_id=user.id, subject="DBMS", semester="4", marks=88, max_marks=100, grade="A+"),
                models.AcademicRecord(student_id=user.id, subject="Operating Systems", semester="4", marks=84, max_marks=100, grade="A"),
                models.AcademicRecord(student_id=user.id, subject="Web Technology", semester="4", marks=92, max_marks=100, grade="S"),
                models.AcademicRecord(student_id=user.id, subject="Design & Analysis of Algorithms", semester="4", marks=86, max_marks=100, grade="A")
            ]
            db.add_all(sample_marks)

        db.commit()

    print(f"Students dataset synchronized successfully: {count_new} created, {count_updated} updated.")


def seed_db():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if base demo users already exist
        if db.query(models.User).count() == 0:
            print("Seeding database with initial college records...")

            # Seed Departments
            depts = [
                models.Department(name="Information Science", code="ISE"),
                models.Department(name="Computer Science", code="CSE"),
                models.Department(name="Electronics & Communication", code="ECE"),
            ]
            db.add_all(depts)
            db.commit()

            # 1. Seed Users
            students = [
                models.User(
                    name="Amrutha S",
                    email="student@uniconnect.edu",
                    role="student",
                    student_id="1AR23IS003",
                    department="Information Science",
                    year="3rd",
                    section="A",
                    dob="2004-08-14",
                    phone="+91 9845012345",
                    gender="Female",
                    blood_group="A+",
                    address="45, 2nd Cross, Malleshwaram, Bangalore"
                ),
                models.User(
                    name="Chandana S",
                    email="student2@uniconnect.edu",
                    role="student",
                    student_id="1AR23IS008",
                    department="Information Science",
                    year="3rd",
                    section="A",
                    dob="2004-12-05",
                    phone="+91 9845098765",
                    gender="Female",
                    blood_group="B+",
                    address="89, 4th Main, Jayanagar, Bangalore"
                )
            ]
            teachers = [
                models.User(
                    name="Prof. Kavya A D",
                    email="teacher@uniconnect.edu",
                    role="teacher",
                    department="Information Science",
                    employee_id="TCH001",
                    designation="Assistant Professor",
                    dob="1985-04-23",
                    phone="+91 9900112233",
                    gender="Female",
                    blood_group="O+",
                    address="12, 1st Main, Rajajinagar, Bangalore"
                )
            ]
            admins = [
                models.User(
                    name="Admin User",
                    email="admin@uniconnect.edu",
                    role="admin"
                )
            ]
            
            all_users = students + teachers + admins
            db.add_all(all_users)
            db.commit()
            
            # Reload student 1 & 2 references to get their auto-incremented primary keys
            student1 = db.query(models.User).filter(models.User.email == "student@uniconnect.edu").first()
            student2 = db.query(models.User).filter(models.User.email == "student2@uniconnect.edu").first()

            # 2. Seed Attendance records for Student 1
            attendance = [
                models.AttendanceRecord(student_id=student1.id, subject="DBMS", date=datetime.date(2025, 3, 5), status="present", percentage=92.0),
                models.AttendanceRecord(student_id=student1.id, subject="ML", date=datetime.date(2025, 3, 4), status="present", percentage=88.0),
                models.AttendanceRecord(student_id=student1.id, subject="Web Tech", date=datetime.date(2025, 3, 3), status="absent", percentage=75.0),
                models.AttendanceRecord(student_id=student1.id, subject="DBMS", date=datetime.date(2025, 3, 1), status="present", percentage=92.0)
            ]
            db.add_all(attendance)

            # 3. Seed Events
            events = [
                models.Event(
                    title="Tech Fest 2025",
                    description="Annual technical symposium with coding competitions and workshops.",
                    date=datetime.date(2025, 3, 15),
                    type="event",
                    venue="Main Auditorium"
                ),
                models.Event(
                    title="Cricket Tournament",
                    description="Inter-class cricket championship.",
                    date=datetime.date(2025, 3, 20),
                    type="sports",
                    venue="College Ground"
                ),
                models.Event(
                    title="Cultural Night",
                    description="Music, dance and drama performances.",
                    date=datetime.date(2025, 3, 25),
                    type="cultural",
                    venue="Open Air Theatre"
                )
            ]
            db.add_all(events)

            # 4. Seed Notices
            notices = [
                models.Notice(
                    title="Mid-semester exam schedule",
                    body="Exams will be held from March 10 to March 18. Hall tickets available on portal.",
                    date=datetime.date(2025, 3, 2),
                    category="Academics"
                ),
                models.Notice(
                    title="Fee payment deadline",
                    body="Last date for fee payment is March 15. Late fee applicable after that.",
                    date=datetime.date(2025, 3, 1),
                    category="Administration"
                )
            ]
            db.add_all(notices)

            # 5. Seed Fees
            fees = [
                models.FeeRecord(student_id=student1.id, amount=45000.0, due_date=datetime.date(2025, 3, 15), status="pending"),
                models.FeeRecord(student_id=student1.id, amount=5000.0, due_date=datetime.date(2025, 2, 28), status="paid", paid_at=datetime.datetime(2025, 2, 25, 10, 0))
            ]
            db.add_all(fees)

            # 6. Seed Academic Records (Marksheet)
            academics = [
                models.AcademicRecord(student_id=student1.id, subject="DBMS", semester="5th", marks=85, max_marks=100, grade="A"),
                models.AcademicRecord(student_id=student1.id, subject="ML", semester="5th", marks=78, max_marks=100, grade="B+"),
                models.AcademicRecord(student_id=student1.id, subject="Web Tech", semester="5th", marks=92, max_marks=100, grade="A")
            ]
            db.add_all(academics)

            # 7. Seed Exam Schedules
            exams = [
                models.ExamSchedule(subject="DBMS", date=datetime.date(2025, 3, 12), time="9:00 AM", venue="Hall A"),
                models.ExamSchedule(subject="ML", date=datetime.date(2025, 3, 14), time="9:00 AM", venue="Hall B"),
                models.ExamSchedule(subject="Web Tech", date=datetime.date(2025, 3, 16), time="2:00 PM", venue="Hall A")
            ]
            db.add_all(exams)

            # 8. Seed Grievances
            grievances = [
                models.Grievance(
                    student_id=student1.id,
                    subject="Library timings",
                    description="Request to extend library hours during exams.",
                    status="resolved",
                    created_at=datetime.datetime(2025, 2, 20, 9, 0),
                    updated_at=datetime.datetime(2025, 2, 25, 16, 0),
                    response="Library will remain open till 8 PM during exam period."
                ),
                models.Grievance(
                    student_id=student1.id,
                    subject="WiFi in hostel",
                    description="Poor connectivity in Block B hostel.",
                    status="in_progress",
                    created_at=datetime.datetime(2025, 3, 1, 14, 30)
                )
            ]
            db.add_all(grievances)

            # 9. Seed Timetable Slots
            timetable_slots = [
                models.TimetableSlot(department="Information Science", year="3rd", section="A", day="Monday", subject="Software Engineering", time_slot="09:00 AM - 10:00 AM", room="LH-201"),
                models.TimetableSlot(department="Information Science", year="3rd", section="A", day="Monday", subject="Database Systems", time_slot="10:15 AM - 11:15 AM", room="Lab-3"),
                models.TimetableSlot(department="Information Science", year="3rd", section="A", day="Tuesday", subject="Machine Learning", time_slot="11:30 AM - 12:30 PM", room="LH-202"),
                models.TimetableSlot(department="Information Science", year="3rd", section="A", day="Wednesday", subject="Web Technology", time_slot="02:00 PM - 03:00 PM", room="Lab-1"),
            ]
            db.add_all(timetable_slots)

            # 10. Seed Subjects
            subjects = [
                models.Subject(name="Software Engineering", code="SE301"),
                models.Subject(name="Database Systems", code="CS302"),
                models.Subject(name="Machine Learning", code="CS303"),
                models.Subject(name="Web Technology", code="CS304"),
            ]
            db.add_all(subjects)

            # 11. Seed Study Materials
            study_materials = [
                models.StudyMaterial(
                    title="Relational Algebra Guide",
                    description="Introductory guide containing syntax, examples, and exercise questions.",
                    file_url="https://w3.impa.br/~vladimir/relalg.pdf",
                    subject="Database Systems",
                    teacher_name="Prof. Kavya A D",
                    department="Information Science",
                    scheme="yearly",
                    year="3rd"
                ),
                models.StudyMaterial(
                    title="Supervised vs Unsupervised ML Cheat Sheet",
                    description="Short summary table explaining regression, classification, and clustering.",
                    file_url="https://web.stanford.edu/~hastie/Papers/ESLII.pdf",
                    subject="Machine Learning",
                    teacher_name="Prof. Kavya A D",
                    department="Information Science",
                    scheme="yearly",
                    year="3rd"
                )
            ]
            db.add_all(study_materials)
            db.commit()
            print("Initial college records seeded successfully.")
        else:
            print("Database already contains base records.")

        # Always synchronize all 58 students from STUDENTS_LIST
        seed_students(db)
        print("Database synchronized successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
