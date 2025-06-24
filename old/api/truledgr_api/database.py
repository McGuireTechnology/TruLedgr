from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sqlite.db")

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Dependency to get a database session
def get_session():
    with Session(engine) as session:
        yield session