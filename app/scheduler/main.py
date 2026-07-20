import time
import logging
from datetime import datetime, timezone
from app.core.database import SessionLocal
from app.models.job import Job, JobStatus
from app.core.redis import redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_scheduler():
    logger.info("Scheduler started. Waking up every 10 seconds to check for ripe jobs...")
    while True:
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            # Find all jobs that are SCHEDULED and their execute_at time has passed
            ripe_jobs = db.query(Job).filter(
                Job.status == JobStatus.SCHEDULED,
                Job.execute_at <= now
            ).all()

            if ripe_jobs:
                logger.info(f"Found {len(ripe_jobs)} ripe jobs. Moving them to QUEUED.")
                for job in ripe_jobs:
                    job.status = JobStatus.QUEUED
                    queue_name = f"queue:{job.priority.value}"
                    redis_client.lpush(queue_name, str(job.id))
                
                db.commit()
                logger.info("Jobs successfully transitioned.")
        except Exception as e:
            logger.error(f"Scheduler Error: {e}")
        finally:
            db.close()
            
        # Sleep until the next check
        time.sleep(10)

if __name__ == "__main__":
    run_scheduler()
