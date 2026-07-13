from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# The Engine is the core interface to the database, responsible for managing connections.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifies the connection is still alive before using it
    pool_size=10,        # Max number of permanent connections
    max_overflow=20      # Max extra connections if pool is full
)

# SessionLocal is a factory for creating new database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy ORM models to inherit from.
Base = declarative_base()

# Dependency function to provide a database session per API request.
# Yields the session so the route can use it, and guarantees it closes when done.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
