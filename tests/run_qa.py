from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qa.evaluator_qa import check_evaluator_sync
from qa.lesson_qa import evaluate_lesson_quality
from reports.qa_reporter import build_report, save_report
from simulation.telegram_simulator import SIM_USERS, TEST_LESSON, run_full_flow_sync
from validators.memory_validator import validate_memory
from validators.progression_validator import validate_progression_state


def main() -> int:
    results = []
    warnings = []
    critical = []

    for cycle in range(2):
        for name, profile in SIM_USERS.items():
            outcome = run_full_flow_sync(profile)
            user = outcome["user"]

            checks = {
                f"{name}: onboarding": bool(user.get("difficulty")),
                f"{name}: profile state": isinstance(user.get("name"), str),
                f"{name}: roadmap valid": len(validate_progression_state(user)) == 0,
                f"{name}: lesson completed": bool(user.get("lesson_finished")),
                f"{name}: xp updated": user.get("xp", 0) > 0,
                f"{name}: streak valid": user.get("streak", 0) >= 1,
                f"{name}: achievements shape": isinstance(user.get("achievements", []), list),
                f"{name}: memory valid": len(validate_memory(user)) == 0,
                f"{name}: duplicate completion blocked": outcome.get("duplicate_completion_safe", False),
                f"{name}: no frozen progression": outcome.get("loops", 0) < 30,
            }

            for label, ok in checks.items():
                results.append((label, ok))
                if not ok:
                    critical.append(f"cycle={cycle + 1} {label}")

            assert user.get("active_lesson") in {None, "jtbd"}
            assert checks[f"{name}: xp updated"] is True
            assert checks[f"{name}: roadmap valid"] is True

    lesson_checks = evaluate_lesson_quality(TEST_LESSON)
    for k, v in lesson_checks.items():
        results.append((f"lesson qa: {k}", v))
        if not v:
            warnings.append(f"lesson qa warning: {k}")

    evaluator_checks = check_evaluator_sync()
    for k, v in evaluator_checks.items():
        results.append((f"evaluator qa: {k}", v))
        if not v:
            critical.append(f"evaluator failure: {k}")

    regression_signals = {
        "onboarding": "onboarding",
        "roadmap": "roadmap valid",
        "lesson engine": "lesson completed",
        "AI evaluator": "evaluator qa:",
        "memory": "memory valid",
        "streak": "streak valid",
        "XP": "xp updated",
        "achievements": "achievements shape",
    }
    for target, signal in regression_signals.items():
        ok = any(signal.lower() in name.lower() and status for name, status in results)
        results.append((f"regression: {target}", ok))

    report = build_report(results, warnings, critical)
    save_report(report)
    save_report(report, "tests/last_qa_report.txt")
    print(report)

    return 1 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
