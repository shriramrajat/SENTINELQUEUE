from pydantic import BaseModel
from typing import Dict

class QueueMetrics(BaseModel):
    high_priority: int
    medium_priority: int
    low_priority: int
    total_waiting: int

class DatabaseMetrics(BaseModel):
    status_counts: Dict[str, int]
    total_tracked: int

class SystemMetrics(BaseModel):
    redis_queues: QueueMetrics
    postgres_jobs: DatabaseMetrics
