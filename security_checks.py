from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent

# Skip dirs with generated/vendor/noise content
SKIP_DIRS = {".git", "__pycache__"}
SKIP_FILES = {".env.example"}

PATTERNS = [
    ("OpenAI-style secret", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("DeepSeek-style secret", re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")),
    ("Telegram token", re.compile(r"\b\d{8,11}:[A-Za-z0-9_-]{30,}\b")),
    ("Hardcoded BOT_TOKEN", re.compile(r"BOT_TOKEN\s*=\s*[\"\'][A-Za-z0-9:_-]{20,}[\"\']")),
    ("Hardcoded API key arg", re.compile(r"api_key\s*=\s*[\"\'](?!your_)[A-Za-z0-9_-]{16,}[\"\']")),
]


def iter_files(base: Path):
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        yield p


def main() -> int:
    violations = []
    for path in iter_files(ROOT):
        # keep scanning only text-like files
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        for label, pattern in PATTERNS:
            for m in pattern.finditer(text):
                if "get_required_env(\"BOT_TOKEN\")" in m.group(0) or "get_required_env(\"DEEPSEEK_API_KEY\")" in m.group(0):
                    continue
                violations.append((path, label, m.group(0)[:120]))

    if violations:
        print("Security check failed. Potential hardcoded secrets found:")
        for path, label, snippet in violations:
            print(f"- {path}: {label}: {snippet}")
        return 1

    print("Security check passed: no obvious hardcoded secrets found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
