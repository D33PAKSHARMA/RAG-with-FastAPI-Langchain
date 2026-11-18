import os
from dotenv import load_dotenv

load_dotenv()

class Settings: 
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "rag_vector_db")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    
    # Internal Docker host vs Localhost check
    DB_HOST = os.getenv("DB_HOST", "localhost")

    DATABASE_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
env = Settings()