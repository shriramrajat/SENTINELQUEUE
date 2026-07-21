import time
import socket
import logging
import uuid
from datetime import datetime, timezone
from app.core.redis import redis_client
from app.core.database import SessionLocal
from app.models.job import Job, JobStatus
from app.workers.tasks import TASK_REGISTRY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WORKER_ID = f"worker-{socket.gethostname()}"
MAX_RETRIES = 3

def process_job(job_id: str):
    db = SessionLocal()
    job = None
    try:
        # Fetch the job from Postgres
        job_uuid = uuid.UUID(job_id)
        job = db.query(Job).filter(Job.id == job_uuid).first()
        if not job:
            logger.error(f"Job {job_id} found in Redis but missing from Postgres!")
            return

        # Distributed Coordination: Mark as running
        if job.status not in [JobStatus.QUEUED, JobStatus.RETRYING]:
            logger.warning(f"Job {job_id} is in status {job.status}. Skipping.")
            return

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        job.worker_id = WORKER_ID
        db.commit()

        # Look up the task function
        task_func = TASK_REGISTRY.get(job.task_name)
        if not task_func:
            raise ValueError(f"Task {job.task_name} is not registered.")

        # Execute
        logger.info(f"Worker {WORKER_ID} executing {job.task_name} (ID: {job_id})")
        task_func(job.payload)

        # Mark as completed
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Job {job_id} COMPLETED.")

    except Exception as e:
        logger.error(f"Job {job_id} FAILED: {str(e)}")
        if job:
            job.error_message = str(e)
            job.retry_count += 1
            if job.retry_count >= MAX_RETRIES:
                job.status = JobStatus.DEAD_LETTER
                logger.error(f"Job {job_id} moved to DEAD_LETTER (Max retries exceeded).")
            else:
                job.status = JobStatus.RETRYING
                # Put it back in the queue
                queue_name = f"queue:{job.priority.value}"
                redis_client.lpush(queue_name, str(job.id))
                logger.info(f"Job {job_id} scheduled for RETRY ({job.retry_count}/{MAX_RETRIES}).")
            db.commit()
    finally:
        db.close()

def run_worker():
    logger.info(f"Starting {WORKER_ID}... Waiting for jobs.")
    while True:
        try:
            # Block for up to 5 seconds waiting for jobs, prioritizing high -> medium -> low
            result = redis_client.brpop(["queue:high", "queue:medium", "queue:low"], timeout=5)
            
            if result:
                queue_name, job_id = result
                process_job(job_id)
                
        except Exception as e:
            logger.error(f"Worker Loop Error: {str(e)}")
            time.sleep(5)  # Prevent tight loop on Redis connection failure

if __name__ == "__main__":
    run_worker()
