from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl, Field
from monitor import check_endpoint
from services.monitoring_service import monitor_multiple_apis


app = FastAPI()


class MonitorRequest(BaseModel):
    url: HttpUrl


class MonitorBatchRequest(BaseModel):
    urls: list[HttpUrl] = Field(min_length=1)


@app.get("/")
def home():
    return {
        "message": "API Monitoring Dashboard Backend is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "project": "API Monitoring Dashboard"
    }


@app.post("/monitor")
def monitor_api(request: MonitorRequest):
    result = check_endpoint(str(request.url))
    return result

@app.post("/monitor/batch")
def monitor_batch(request: MonitorBatchRequest):
    return monitor_multiple_apis(request.urls)