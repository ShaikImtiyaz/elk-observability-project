import json
import logging
import random
import time
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Response

app = FastAPI(title="Enterprise API Monitoring Demo", version="1.0.0")

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            **getattr(record, "fields", {})
        })

logger = logging.getLogger("api_monitor")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/api.jsonl")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.propagate = False

def simulate_request(api_name: str, response: Response):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    # Simulate backend processing time.
    time.sleep(random.uniform(0.05, 0.4))

    # Simulate occasional integration failures.
    failed = random.random() < 0.20
    status_code = 503 if failed else 200
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    event = {
        "service": "integration-monitor",
        "api_name": api_name,
        "request_id": request_id,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "environment": "development"
    }

    logger.log(
        logging.ERROR if failed else logging.INFO,
        "API request completed",
        extra={"fields": event}
    )

    response.status_code = status_code
    return {
        "request_id": request_id,
        "api": api_name,
        "status": "error" if failed else "success",
        "status_code": status_code,
        "duration_ms": duration_ms
    }

@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/api/orders")
def orders(response: Response):
    return simulate_request("orders", response)

@app.get("/api/payments")
def payments(response: Response):
    return simulate_request("payments", response)
