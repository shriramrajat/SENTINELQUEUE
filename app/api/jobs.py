from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse
from app.core.redis import redis_client

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    # 1. Write to Postgres (The permanent record)
    new_job = Job(
        task_name=job_in.task_name,
        payload=job_in.payload,
        priority=job_in.priority
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # 2. Push to Redis queue based on priority (e.g., 'queue:high')
    queue_name = f"queue:{new_job.priority.value}"
    
    # We push just the Job ID. The worker fetches details from Postgres.
    redis_client.lpush(queue_name, str(new_job.id))
    
    # 3. Return instantly
    return new_job

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
