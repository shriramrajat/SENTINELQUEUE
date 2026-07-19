import time
import logging

logger = logging.getLogger(__name__)

def generate_pdf(payload: dict):
    logger.info(f"Generating PDF for {payload.get('user_id', 'unknown')}")
    time.sleep(5)  # Simulate heavy work
    if payload.get("force_fail"):
        raise Exception("Failed to generate PDF due to forced error!")
    logger.info("PDF generation complete.")
    return {"status": "success", "file": "s3://bucket/path.pdf"}

def send_email(payload: dict):
    logger.info(f"Sending email to {payload.get('to', 'unknown')}")
    time.sleep(2)
    logger.info("Email sent.")
    return {"status": "success", "delivered_at": time.time()}

# Task Registry
TASK_REGISTRY = {
    "generate_pdf": generate_pdf,
    "send_email": send_email
}
