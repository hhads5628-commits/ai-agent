#!/usr/bin/env python3
"""Fail if merge-conflict markers are present in tracked source files."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MARKERS = ("<<<<<<<", "=======", ">>>>>>>")
SCAN_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml"}


def tracked_files() -> list[Path]:
    out = subprocess.check_output(["git", "ls-files"], text=True)
    paths = [Path(line.strip()) for line in out.splitlines() if line.strip()]
    return [p for p in paths if p.suffix.lower() in SCAN_EXTENSIONS]


def main() -> int:
    bad = []
    for path in tracked_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for idx, line in enumerate(text.splitlines(), start=1):
            if line.startswith(MARKERS):
                bad.append((path, idx, line.strip()))

    if not bad:
        print("OK: merge-conflict markers not found.")
        return 0

    print("ERROR: merge-conflict markers found:")
    for path, line_no, line in bad:
        print(f" - {path}:{line_no}: {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
