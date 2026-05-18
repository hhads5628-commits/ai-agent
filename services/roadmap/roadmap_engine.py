def summarize_progress(analytics):
    answered = len(analytics)
    passed = len([row for row in analytics if row.get("success")])
    avg_coverage = 0

    if answered:
        coverage_sum = 0
        for row in analytics:
            expected = row.get("expected", 0)
            matched = row.get("matched", 0)
            if expected > 0:
                coverage_sum += int((matched / expected) * 100)
            else:
                coverage_sum += 100

        avg_coverage = int(coverage_sum / answered)

    return {
        "answered": answered,
        "passed": passed,
        "avg_coverage": avg_coverage,
    }
