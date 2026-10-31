
import time
import httpx
import math

LATENCY_THRESHOLD_MS = 1500

def get_latency_status(latency_ms):

    if latency_ms > LATENCY_THRESHOLD_MS:
        return "Slow"
    else:
        return "Normal"


def check_endpoint(url):

    if not url:
        raise ValueError("URL cannot be empty")

    start_time = time.perf_counter()

   

    try:
        response = httpx.get(url, timeout=5.0)
        latency_ms = (time.perf_counter() - start_time) * 1000

        return {
           "url": url,
            "status_code": response.status_code,
            "latency_ms": round(latency_ms, 2),
            "latency_status": get_latency_status(latency_ms),
            "success": response.is_success,
            "error": None,
        }

    except httpx.TimeoutException:
        latency_ms = (time.perf_counter() - start_time) * 1000

        return {
            "url": url,
            "status_code": None,
            "latency_ms": round(latency_ms, 2),
            "latency_status": get_latency_status(latency_ms),
            "success": False,
            "error": "Timeout",
        }

    except httpx.RequestError as error:
        latency_ms = (time.perf_counter() - start_time) * 1000

        return {
            "url": url,
            "status_code": None,
            "latency_ms": round(latency_ms, 2),
            "latency_status": get_latency_status(latency_ms),
            "success": False,
            "error": type(error).__name__,
          
        }


def generate_summary(results):

    successful = 0
    failed = 0

    for result in results:
        if result["success"]:
            successful += 1
        else:
            failed += 1

    total = len(results)

    if total > 0:
        success_rate = (successful / total) * 100
    else:
        success_rate = 0

    # Calculate average latency
    total_latency = 0

    for result in results:
        total_latency += result["latency_ms"]

    if total > 0:
        average_latency = total_latency / total
    else:
        average_latency = 0

    # Calculate minimum and maximum latency
    if total > 0:
        latencies = [result["latency_ms"] for result in results]

        minimum_latency = min(latencies)
        maximum_latency = max(latencies)

    else:
        minimum_latency = 0
        maximum_latency = 0
    # Calculate P95 latency
    if total > 0:
        sorted_latencies = sorted(latencies)

        p95_position = math.ceil(0.95 * total)

        p95_latency = sorted_latencies[p95_position - 1]

    else:
        p95_latency = 0


    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": round(success_rate, 2),
        "average_latency_ms": round(average_latency, 2),
        "minimum_latency_ms": round(minimum_latency, 2),
        "maximum_latency_ms": round(maximum_latency, 2),
        "p95_latency_ms": round(p95_latency, 2)
    }
    

def main():

    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/status/500",
    ]

    results = []

    for url in urls:
        result = check_endpoint(url)
        results.append(result)

        print(result)

    summary = generate_summary(results)

    print("\nMONITORING SUMMARY")
    print("------------------")
    print("Total APIs:", summary["total"])
    print("Successful:", summary["successful"])
    print("Failed:", summary["failed"])
    print("Success Rate:", summary["success_rate"], "%")
    print("Average Latency:", summary["average_latency_ms"], "ms")
    print("Minimum Latency:", summary["minimum_latency_ms"], "ms")
    print("Maximum Latency:", summary["maximum_latency_ms"], "ms")
    print("P95 Latency:", summary["p95_latency_ms"], "ms")


if __name__ == "__main__":
    main()
