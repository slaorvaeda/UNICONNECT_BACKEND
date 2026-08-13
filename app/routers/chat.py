from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import models, schemas, config
from openai import OpenAI

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize OpenAI
client = OpenAI(api_key=config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None

@router.post("/chat")
async def chat_assistant(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        # 1. Fetch student info (default to Amrutha S, the first student user in DB)
        student = db.query(models.User).filter(models.User.role == "student").first()
        
        # 2. Query other data tables dynamically for the student's records
        student_id = student.id if student else None
        
        attendance = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.student_id == student_id).all() if student_id else []
        fees = db.query(models.FeeRecord).filter(models.FeeRecord.student_id == student_id).all() if student_id else []
        academics = db.query(models.AcademicRecord).filter(models.AcademicRecord.student_id == student_id).all() if student_id else []
        grievances = db.query(models.Grievance).filter(models.Grievance.student_id == student_id).all() if student_id else []
        
        notices = db.query(models.Notice).all()
        events = db.query(models.Event).all()
        exams = db.query(models.ExamSchedule).all()
        
        timetable = []
        if student:
            timetable = db.query(models.TimetableSlot).filter(
                models.TimetableSlot.department == student.department,
                models.TimetableSlot.year == student.year,
                models.TimetableSlot.section == student.section
            ).all()

        # 3. Format database records into a rich context prompt string
        student_name = student.name if student else "Student"
        student_code = student.student_id if student else "Unknown ID"
        student_yr = student.year if student else "Unknown Year"
        student_dept = student.department if student else "Unknown Dept"
        
        attendance_str = "\n".join([f"- {r.subject}: {r.percentage}% (Status: {r.status} on {r.date})" for r in attendance]) or "No attendance logs found."
        fees_str = "\n".join([f"- Amount: ₹{r.amount:.0f}, Due: {r.due_date}, Status: {r.status.upper()}" + (f" (Paid on {r.paid_at.date()})" if r.paid_at else "") for r in fees]) or "No fee records found."
        academics_str = "\n".join([f"- {r.subject} ({r.semester} sem): Marks {r.marks}/{r.max_marks}, Grade {r.grade}" for r in academics]) or "No academic grades recorded."
        grievances_str = "\n".join([f"- '{r.subject}' Status: {r.status.upper()} (Created: {r.created_at.date()})" + (f", Response: '{r.response}'" if r.response else "") for r in grievances]) or "No grievances submitted."
        notices_str = "\n".join([f"- '{r.title}' ({r.date}): '{r.body}'" for r in notices]) or "No notices posted."
        events_str = "\n".join([f"- '{r.title}' ({r.date}), Venue: '{r.venue}' - {r.description}" for r in events]) or "No upcoming events scheduled."
        exams_str = "\n".join([f"- '{r.subject}' ({r.date} at {r.time}), Venue: '{r.venue}'" for r in exams]) or "No exams scheduled."
        timetable_str = "\n".join([f"- {r.day}: {r.subject} at {r.time_slot}" + (f" in Room {r.room}" if r.room else "") for r in timetable]) or "No class timetable slots scheduled."

        import datetime
        current_date_str = datetime.date.today().strftime("%B %d, %Y")
        current_day_str = datetime.date.today().strftime("%A")

        dynamic_campus_context = f"""
You are Junuh, the AI chatbot for UniConnect (the Smart College App) at Amruta Institute of Engineering and Management Sciences, Department of Information Science.
You are helping {student_name} (Student ID: {student_code}, Year: {student_yr}, Department: {student_dept}).

Here is the student's dynamic database records loaded in real-time. Use ONLY these details to answer user queries:

[CURRENT TIME CONTEXT]
- Today's Date: {current_date_str}
- Today's Day of Week: {current_day_str}

[COLLEGE INFO]
- Institution: Amruta Institute of Engineering and Management Sciences
- Guided by: Prof. Kavya A D, Assistant Professor, Department of Information Science

[STUDENT PROFILE]
- Name: {student_name}
- Student ID: {student_code}
- Department: {student_dept}
- Year: {student_yr}

[ATTENDANCE RECORDS]
{attendance_str}

[ACADEMIC RECORDS]
{academics_str}

[EXAM SCHEDULES]
{exams_str}

[FEE RECORDS]
{fees_str}

[GRIEVANCES LOG]
{grievances_str}

[OFFICIAL NOTICES]
{notices_str}

[UPCOMING EVENTS & SPORTS]
{events_str}

[CLASS TIMETABLE SCHEDULES]
{timetable_str}


[INSTRUCTIONS]
1. Use the provided context to answer questions about the student's profile, grades, attendance, fees, grievances, notices, exams, and campus events. 
2. If the user asks general academic, language, or tutoring questions (e.g. "What is Java?", "What is OOPs?", "Explain DBMS"), explain them shortly and simply using basic terminology. Keep responses extremely brief (max 2-3 sentences or a short bulleted list).
3. For specific campus operational details not mentioned in the context (e.g. "where is the dean's office?"), politely tell them you do not have that specific information in the context and suggest contacting Prof. Kavya A D or the administrative office.
4. Keep all responses very short, direct, friendly, and helpful to save tokens.
5. Be encouraging about academic performance and prompt them regarding pending deadlines (like pending tuition fees or low attendance cutoffs).
"""

        # 4. Handle Mock/Fallback if OpenAI is not set
        if not client or not config.OPENAI_API_KEY:
            print("WARNING: OpenAI API key is missing. Returning database-driven fallback response.")
            user_msg = request.messages[-1].content.lower() if request.messages else ""
            reply = "Hello! I am your UniConnect Assistant. (Note: OpenAI API Key is not configured on the server, showing database-driven fallback response).\n\n"
            
            if "exam" in user_msg or "test" in user_msg:
                reply += f"Based on the database, here are your exam schedules:\n{exams_str}"
            elif "timetable" in user_msg or "schedule" in user_msg or "class" in user_msg:
                reply += f"Here are your class timetable schedules:\n{timetable_str}"
            elif "attendance" in user_msg:
                reply += f"According to database attendance records:\n{attendance_str}"
            elif "fee" in user_msg or "pay" in user_msg:
                reply += f"Here are your financial fee status details:\n{fees_str}"
            elif "event" in user_msg or "fest" in user_msg:
                reply += f"Here are the upcoming events and cultural sports programs:\n{events_str}"
            elif "wifi" in user_msg or "grievance" in user_msg:
                reply += f"Your current database grievance tickets:\n{grievances_str}"
            elif "notice" in user_msg:
                reply += f"Here are the latest announcements:\n{notices_str}"
            elif "grade" in user_msg or "marks" in user_msg:
                reply += f"Here are your academic grades:\n{academics_str}"
            else:
                reply += f"Welcome {student_name}! I can query the SQLite database to tell you about your class timetable, attendance, exam schedules, events, notices, grievances, or fee statuses. What would you like to know?"
            
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": reply
                    }
                }]
            }

        # 5. Build chat history and call OpenAI
        api_messages = [{"role": "system", "content": dynamic_campus_context}]
        for msg in request.messages:
            role = "user" if msg.role == "user" else "assistant"
            api_messages.append({"role": role, "content": msg.content})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_messages,
            temperature=0.7,
            max_tokens=150,
        )

        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response.choices[0].message.content
                }
            }]
        }

    except Exception as e:
        print(f"Error in chat assistant router: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with AI assistant: {str(e)}"
        )
