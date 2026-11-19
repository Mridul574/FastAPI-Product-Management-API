from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base , sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing!")

engine = create_engine(DATABASE_URL)

Base= declarative_base()

SessionLocal= sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

try:
    with engine.connect() as connection:
        print("succes")
except Exception as e:
    print("failed",e)