#!/usr/bin/env bash
set -euo pipefail
mkdir -p .git/hooks
cat > .git/hooks/pre-push <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
python tests/run_qa.py || {
  echo "❌ QA failed. Push blocked. See reports/qa_report.txt"
  exit 1
}
HOOK
chmod +x .git/hooks/pre-push
echo "✅ pre-push QA hook installed"
