import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"

class JobPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    task_name = Column(String, index=True, nullable=False)
    payload = Column(JSON, nullable=False, default={})
    
    status = Column(Enum(JobStatus), default=JobStatus.QUEUED, index=True, nullable=False)
    priority = Column(Enum(JobPriority), default=JobPriority.MEDIUM, index=True, nullable=False)
    
    execute_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    retry_count = Column(Integer, default=0, nullable=False)
    worker_id = Column(String, nullable=True, index=True)
    error_message = Column(Text, nullable=True)
