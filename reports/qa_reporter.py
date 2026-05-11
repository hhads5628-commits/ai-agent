from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def build_report(results: list[tuple[str, bool]], warnings: list[str], critical: list[str]) -> str:
    total = len(results)
    passed = sum(1 for _, ok in results if ok)
    score = int((passed / total) * 100) if total else 0

    lines = [
        "================================",
        "AI PRODUCT SCHOOL QA REPORT",
        "===========================",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    for name, ok in results:
        lines.append(f"{'✅' if ok else '❌'} {name}")

    lines += [
        "",
        f"Critical Issues: {len(critical)}",
        f"Warnings: {len(warnings)}",
        f"QA Score: {score}/100",
    ]

    if critical:
        lines.append("\nCritical details:")
        lines.extend(f"- {x}" for x in critical)

    if warnings:
        lines.append("\nWarnings:")
        lines.extend(f"- {x}" for x in warnings)

    return "\n".join(lines) + "\n"


def save_report(text: str, path: str = "reports/qa_report.txt") -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p
