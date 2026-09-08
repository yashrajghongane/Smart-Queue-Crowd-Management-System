import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Default to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./queue.db")

engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite concurrency configurations
    engine_args["connect_args"] = {"check_same_thread": False, "timeout": 15}
    engine_args["poolclass"] = StaticPool # Useful for in-memory / testing, safely managing SQLite connections

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
