import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

PORT = int(os.getenv("PORT", 5001))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./uniconnect.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

