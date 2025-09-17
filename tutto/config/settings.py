import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB Configuration
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "tuttoDb")
