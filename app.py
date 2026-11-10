from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl, Field
from monitor import check_endpoint, generate_summary


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
def monitor_multiple_apis(request: MonitorBatchRequest):

    results = []

    for url in request.urls:
        result = check_endpoint(str(url))
        results.append(result)

    summary = generate_summary(results)

    return {
    "summary": summary,
    "results": results
}