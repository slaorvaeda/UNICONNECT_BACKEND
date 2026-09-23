import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import auth, student, chat, admin, teacher
from app.core.config import PORT

from app.seed import seed_db

# Automatically create tables in local SQLite/PostgreSQL
Base.metadata.create_all(bind=engine)
try:
    seed_db()
except Exception as e:
    print(f"Seed note: {e}")

app = FastAPI(
    title="UniConnect Smart College App API",
    description="Modular database-driven API with integrated AI chatbot",
    version="1.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Router Modules
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(teacher.router, prefix="/api/teacher", tags=["teacher"])

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "UniConnect Database-Driven Modular Backend is active!",
        "version": "1.1.0"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
