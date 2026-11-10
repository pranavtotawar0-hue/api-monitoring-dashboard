
from fastapi import FastAPI
from pydantic import BaseModel
from monitor import check_endpoint

app = FastAPI()
class MonitorRequest(BaseModel):
    url: str


@app.get("/")
def home():
    return {
        "message": "API Monitoring Dashboard Backend is running!"
    }
@app.get("/health")
def health() :
    return {
        "status": "healthy",
        "project": "API Monitoring Dashboard"
    }
@app.post("/monitor")
def monitor_api(request: MonitorRequest):
    result = check_endpoint(request.url)

    return result