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
        # 1. Fetch student info dynamically by passed student_id or default to first student
        student = None
        if request.student_id:
            student = db.query(models.User).filter(models.User.id == request.student_id).first()
        if not student:
            student = db.query(models.User).filter(models.User.role == "student").first()
        
        # 2. Query data tables dynamically for this specific student
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

        # 3. Format database records into rich context strings
        student_name = student.name if student else "Student"
        student_code = student.student_id if student else "1AR23IS003"
        student_yr = student.year if student else "3rd Year"
        student_dept = student.department if student else "Information Science"
        student_sec = student.section if student else "A"
        
        attendance_str = "\n".join([f"• {r.subject}: {r.percentage}% (Latest status: {r.status.upper()} on {r.date})" for r in attendance]) or "No attendance logs found."
        fees_str = "\n".join([f"• ₹{r.amount:,.0f} | Due: {r.due_date} | Status: {r.status.upper()}" + (f" (Paid on {r.paid_at.date()})" if r.paid_at else "") for r in fees]) or "No fee records found."
        academics_str = "\n".join([f"• {r.subject} ({r.semester} Sem): Marks {r.marks}/{r.max_marks} | Grade: {r.grade}" for r in academics]) or "No academic grades recorded."
        grievances_str = "\n".join([f"• [{r.status.upper()}] '{r.subject}' (Submitted: {r.created_at.date()})" + (f"\n  Response: {r.response}" if r.response else "") for r in grievances]) or "No grievances submitted."
        notices_str = "\n".join([f"• [{r.category}] {r.title} ({r.date}):\n  \"{r.body}\"" for r in notices]) or "No notices posted."
        events_str = "\n".join([f"• {r.title} ({r.date}) @ {r.venue}\n  {r.description}" for r in events]) or "No upcoming events scheduled."
        exams_str = "\n".join([f"• {r.subject}: {r.date} at {r.time} (Venue: {r.venue})" for r in exams]) or "No exams scheduled."
        timetable_str = "\n".join([f"• {r.day}: {r.subject} ({r.time_slot})" + (f" in Room {r.room}" if r.room else "") for r in timetable]) or "No class timetable slots scheduled."

        import datetime
        current_date_str = datetime.date.today().strftime("%B %d, %Y")
        current_day_str = datetime.date.today().strftime("%A")

        dynamic_campus_context = f"""
You are Junuh, the AI smart assistant for UniConnect at Amruta Institute of Engineering and Management Sciences, Department of Information Science.
You are helping {student_name} (ID: {student_code}, Year: {student_yr}, Department: {student_dept}, Section: {student_sec}).

[CAMPUS CONTEXT]
- College: Amruta Institute of Engineering and Management Sciences, Bangalore
- Faculty Guide: Prof. Kavya A D (Assistant Professor, Dept of ISE)
- Today: {current_day_str}, {current_date_str}

[STUDENT PROFILE]
- Name: {student_name} | ID: {student_code} | Dept: {student_dept} | Year: {student_yr} | Section: {student_sec}

[ATTENDANCE]
{attendance_str}

[EXAMS]
{exams_str}

[ACADEMICS & GRADES]
{academics_str}

[TIMETABLE]
{timetable_str}

[FEES]
{fees_str}

[NOTICES]
{notices_str}

[EVENTS]
{events_str}

[GRIEVANCES]
{grievances_str}

Instructions: Keep answers concise, clear, helpful, and friendly.
"""

        # 4. Smart Local Knowledge & Conversational Engine (Fallback)
        def generate_smart_response():
            # Get latest user message
            user_msg = ""
            for msg in reversed(request.messages):
                if msg.role == "user":
                    user_msg = msg.content.strip().lower()
                    break

            # Greetings & conversational
            if user_msg in ["hi", "hello", "hey", "hola", "namaste", "good morning", "good afternoon", "good evening", "sup", "yo"]:
                return f"Hello {student_name}! 👋 Great to chat with you. How can I help you today? You can ask me about your exams, timetable, attendance, marks, fees, or events!"
            
            if any(k in user_msg for k in ["how are you", "how r u", "how do you do", "what's up", "whats up"]):
                return f"I'm doing great, {student_name}! 🚀 Ready to assist you with your academics, timetable, exam schedules, and campus updates. What would you like to check?"

            if any(k in user_msg for k in ["who are you", "what is your name", "who made you", "what are you"]):
                return f"I am Junuh, your AI campus companion for UniConnect at Amruta Institute of Engineering and Management Sciences! I'm designed to help you check your attendance, exam schedules, class routines, fees, circulars, and study info."

            if any(k in user_msg for k in ["help", "what can you do", "features", "options", "commands"]):
                return f"Here is what I can assist you with:\n\n📅 Exam Schedules — Ask \"When is my DBMS exam?\"\n📊 Attendance — Ask \"What is my attendance?\"\n🗓️ Timetable — Ask \"What classes do I have?\"\n🎓 Grades — Ask \"Show my marks\"\n💰 Fees — Ask \"Check pending fees\"\n📢 Notices — Ask \"Show latest notices\"\n🏆 Events — Ask \"Upcoming college events\"\n💬 Grievances — Ask \"Check grievance status\""

            if any(k in user_msg for k in ["who am i", "my profile", "my details", "my name", "my usn", "my id", "about me"]):
                return f"📋 **Your Profile Details:**\n• **Name:** {student_name}\n• **Student ID / USN:** {student_code}\n• **Department:** {student_dept}\n• **Year / Section:** {student_yr} Year (Section {student_sec})\n• **Phone:** {student.phone if student and student.phone else 'N/A'}\n• **Blood Group:** {student.blood_group if student and student.blood_group else 'N/A'}"

            # Exam queries
            if any(k in user_msg for k in ["exam", "test", "midsem", "finals", "seating", "hall ticket"]):
                return f"📝 **Upcoming Exam Schedules:**\n{exams_str}\n\n💡 *Tip: Make sure to arrive at the venue 15 minutes before exam time!*"

            # Timetable queries
            if any(k in user_msg for k in ["timetable", "schedule", "class", "routine", "period", "lecture"]):
                return f"🗓️ **Class Timetable Slots:**\n{timetable_str}"

            # Attendance queries
            if any(k in user_msg for k in ["attendance", "present", "absent", "percentage", "cutoff", "bunk"]):
                return f"📊 **Subject Attendance Summary:**\n{attendance_str}\n\n📌 *Reminder: A minimum of 75% attendance is required in each subject to be eligible for semester exams.*"

            # Fee queries
            if any(k in user_msg for k in ["fee", "fees", "pay", "due", "tuition", "receipt", "fine"]):
                return f"💳 **Fee Status & Dues:**\n{fees_str}\n\n💳 You can make payments directly under the **Fees** tab in the app."

            # Events queries
            if any(k in user_msg for k in ["event", "fest", "sports", "cricket", "cultural", "tournament", "activities"]):
                return f"🎉 **Upcoming Campus Events & Sports:**\n{events_str}"

            # Notice queries
            if any(k in user_msg for k in ["notice", "announcement", "circular", "news", "update"]):
                return f"📢 **Latest Official Circulars:**\n{notices_str}"

            # Marks and Grade queries
            if any(k in user_msg for k in ["grade", "marks", "result", "sgpa", "cgpa", "score"]):
                return f"🎓 **Academic Records & Grades:**\n{academics_str}"

            # Grievance queries
            if any(k in user_msg for k in ["grievance", "complaint", "ticket", "issue", "problem"]):
                return f"📨 **Your Grievance Tickets:**\n{grievances_str}\n\n✏️ To submit a new grievance, use the **Grievances** tab."

            # Faculty & College Info
            if any(k in user_msg for k in ["teacher", "faculty", "professor", "kavya", "guide", "hod", "mentor"]):
                return "👩‍🏫 **Department Faculty:**\n• **Prof. Kavya A D** — Assistant Professor, Department of Information Science & Engineering\n• Dedicated guide for the UniConnect Smart College initiative."

            if any(k in user_msg for k in ["college", "amruta", "institute", "aiems", "campus"]):
                return "🏛️ **Amruta Institute of Engineering and Management Sciences (AIEMS):**\nLocated in Bangalore, dedicated to engineering excellence, technical innovation, and holistic student development."

            # Educational/Technical concepts
            if "dbms" in user_msg or "database" in user_msg or "sql" in user_msg:
                return "🗄️ **Database Management Systems (DBMS):**\nA software system used to define, manipulate, retrieve, and manage data efficiently (e.g., PostgreSQL, SQLite, MySQL). In SQL, data is organized in structured tables with primary & foreign keys."

            if "ml" in user_msg or "machine learning" in user_msg or "ai" in user_msg:
                return "🤖 **Machine Learning & AI:**\nA branch of computer science focused on building algorithms that learn patterns from data to make predictions or decisions without explicit programming."

            if "python" in user_msg:
                return "🐍 **Python:**\nA versatile, high-level, interpreted programming language widely used in AI/ML, backend web development (like our FastAPI server), automation, and data analysis."

            if "java" in user_msg:
                return "☕ **Java:**\nA class-based, object-oriented programming language designed with the 'Write Once, Run Anywhere' (WORA) philosophy, popular in enterprise software and Android apps."

            # Default conversational fallback
            return f"I understand you're asking about '{user_msg}'.\n\nAs your UniConnect assistant, I have real-time access to your **exams**, **attendance**, **timetable**, **fees**, **grades**, and **campus notices**. Could you clarify which of these you'd like to check?"

        # 5. Try OpenAI first if configured
        if client and config.OPENAI_API_KEY:
            try:
                api_messages = [{"role": "system", "content": dynamic_campus_context}]
                for msg in request.messages:
                    role = "user" if msg.role == "user" else "assistant"
                    api_messages.append({"role": role, "content": msg.content})

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=api_messages,
                    temperature=0.7,
                    max_tokens=250,
                )
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": response.choices[0].message.content
                        }
                    }]
                }
            except Exception as ai_err:
                print(f"OpenAI call error ({ai_err}). Seamlessly using smart database fallback.")

        # 6. Return smart conversational response
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": generate_smart_response()
                }
            }]
        }

    except Exception as e:
        print(f"Error in chat assistant router: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with AI assistant: {str(e)}"
        )

