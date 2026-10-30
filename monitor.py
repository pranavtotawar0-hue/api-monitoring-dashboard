
import time
import httpx


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
            "success": response.is_success,
            "error": None,
        }

    except httpx.TimeoutException:
        latency_ms = (time.perf_counter() - start_time) * 1000

        return {
            "url": url,
            "status_code": None,
            "latency_ms": round(latency_ms, 2),
            "success": False,
            "error": "Timeout",
        }

    except httpx.RequestError as error:
        latency_ms = (time.perf_counter() - start_time) * 1000

        return {
            "url": url,
            "status_code": None,
            "latency_ms": round(latency_ms, 2),
            "success": False,
            "error": type(error).__name__,
        }


def main():
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/status/500",
    ]

    for url in urls:
        result = check_endpoint(url)
        print(result)


if __name__ == "__main__":
    main()
