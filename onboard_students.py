import os
import sys
import datetime
import openpyxl

# Add parent directory to sys.path so app modules import properly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.core import models

EXCEL_PATH = "/Users/priyanshunayak/Desktop/Unnionnet/Student_Details_174_to_231.xlsx"

# Known author USN mapping
KNOWN_USNS = {
    "AMRUTHA.S": "1AR23IS003",
    "CHANDANA.S": "1AR23IS008",
    "CHANNAVEER MATRANGI": "1AR23IS009",
    "NIVEDITHA.C.A": "1AR23IS028",
    "OMKAR.T.P": "1AR23IS029",
}

def clean_str(val):
    return str(val).strip() if val is not None else None

def onboard_students():
    print(f"Loading Excel file: {EXCEL_PATH}")
    wb = openpyxl.load_workbook(EXCEL_PATH)
    sheet = wb.active

    db = SessionLocal()
    try:
        rows = list(sheet.iter_rows(values_only=True))
        headers = rows[0]
        print(f"Detected Headers: {headers}")
        student_rows = rows[1:]
        print(f"Total Student records to process: {len(student_rows)}")

        onboarded_list = []

        for idx, row in enumerate(student_rows, start=1):
            name, dob, address, phone, gender, email = row
            name_str = clean_str(name)
            if not name_str:
                continue

            dob_str = clean_str(dob)
            address_str = clean_str(address)
            phone_str = clean_str(phone)
            gender_code = clean_str(gender)
            gender_full = "Female" if gender_code and gender_code.upper() == "F" else "Male"
            email_str = clean_str(email)

            # Generate fallback email if missing in Excel
            if not email_str:
                slug = name_str.lower().replace(" ", "").replace(".", "")
                email_str = f"{slug}@uniconnect.edu"

            # Compute password from DOB (e.g. 08.09.2005 -> 08092005)
            clean_pwd = dob_str.replace(".", "").replace("-", "").replace("/", "").replace(" ", "") if dob_str else "123456"

            # Roll Number / USN: 174 to 231
            serial_num = 174 + (idx - 1)
            usn = KNOWN_USNS.get(name_str, f"1AR23IS{serial_num:03d}")

            # Check if user already exists by email or student_id
            user = db.query(models.User).filter(
                (models.User.email == email_str) | (models.User.student_id == usn)
            ).first()

            if not user:
                user = models.User(
                    name=name_str,
                    email=email_str,
                    role="student",
                    student_id=usn,
                    department="Information Science",
                    year="3rd",
                    section="A",
                    dob=dob_str,
                    phone=phone_str,
                    gender=gender_full,
                    blood_group="O+",
                    address=address_str
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                status_text = "NEWLY CREATED"
            else:
                # Update profile fields with Excel data
                user.name = name_str
                user.dob = dob_str
                user.phone = phone_str
                user.address = address_str
                user.gender = gender_full
                user.department = "Information Science"
                user.year = "3rd"
                user.section = "A"
                db.commit()
                status_text = "UPDATED"

            # ------------------ ONBOARD REGARDING DATA ------------------
            # 1. Attendance Records
            existing_att = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.student_id == user.id).count()
            if existing_att == 0:
                sample_att = [
                    models.AttendanceRecord(student_id=user.id, subject="Database Management Systems", date=datetime.date(2025, 3, 10), status="present", percentage=91.5),
                    models.AttendanceRecord(student_id=user.id, subject="Machine Learning", date=datetime.date(2025, 3, 9), status="present", percentage=88.0),
                    models.AttendanceRecord(student_id=user.id, subject="Web Technology & Applications", date=datetime.date(2025, 3, 8), status="present", percentage=85.0),
                    models.AttendanceRecord(student_id=user.id, subject="Operating Systems", date=datetime.date(2025, 3, 7), status="present", percentage=93.0),
                ]
                db.add_all(sample_att)

            # 2. Fee Records
            existing_fees = db.query(models.FeeRecord).filter(models.FeeRecord.student_id == user.id).count()
            if existing_fees == 0:
                sample_fees = [
                    models.FeeRecord(student_id=user.id, amount=45000.0, due_date=datetime.date(2026, 11, 30), status="pending"),
                    models.FeeRecord(student_id=user.id, amount=5000.0, due_date=datetime.date(2026, 8, 15), status="paid", paid_at=datetime.datetime(2026, 8, 10, 10, 30))
                ]
                db.add_all(sample_fees)

            # 3. Academic Records (Marks & Grades)
            existing_marks = db.query(models.AcademicRecord).filter(models.AcademicRecord.student_id == user.id).count()
            if existing_marks == 0:
                sample_marks = [
                    models.AcademicRecord(student_id=user.id, subject="DBMS", semester="4", marks=88, max_marks=100, grade="A+"),
                    models.AcademicRecord(student_id=user.id, subject="Operating Systems", semester="4", marks=84, max_marks=100, grade="A"),
                    models.AcademicRecord(student_id=user.id, subject="Web Technology", semester="4", marks=92, max_marks=100, grade="S"),
                    models.AcademicRecord(student_id=user.id, subject="Design & Analysis of Algorithms", semester="4", marks=86, max_marks=100, grade="A")
                ]
                db.add_all(sample_marks)

            db.commit()

            onboarded_list.append({
                "index": idx,
                "serial": serial_num,
                "name": name_str,
                "usn": usn,
                "email": email_str,
                "dob": dob_str,
                "password": clean_pwd,
                "status": status_text
            })

        print(f"\n=======================================================")
        print(f"SUCCESS: {len(onboarded_list)} Students Successfully Processed into Database!")
        print(f"=======================================================\n")
        
        # Print first 10 for immediate confirmation
        for s in onboarded_list[:10]:
            print(f"[{s['serial']}] {s['name']} | USN: {s['usn']} | Email: {s['email']} | Password: {s['password']}")

    finally:
        db.close()

if __name__ == "__main__":
    onboard_students()
