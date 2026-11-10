from monitor import check_endpoint, generate_summary


def monitor_multiple_apis(urls):

    results = []

    for url in urls:
        result = check_endpoint(str(url))
        results.append(result)

    summary = generate_summary(results)

    return {
        "summary": summary,
        "results": results
    }