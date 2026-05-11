import asyncio
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.test_qa_system import run_all_tests, print_report

if __name__ == "__main__":
    report = asyncio.run(run_all_tests())
    print_report(report)
