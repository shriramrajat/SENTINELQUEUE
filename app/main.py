from fastapi import FastAPI
from app.api import jobs

app = FastAPI(title="SentinelQueue Gateway")

app.include_router(jobs.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
