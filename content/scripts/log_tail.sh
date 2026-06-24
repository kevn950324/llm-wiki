#!/usr/bin/env bash
# log_tail.sh — 顯示 log.md 最近 N 筆 entry，避免讀整份 log
# Usage: log_tail.sh [n=10]
set -euo pipefail

N="${1:-10}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WIKI_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG="$WIKI_ROOT/proceed/1.log/log.md"

[[ -f "$LOG" ]] || { echo "log.md 不存在：$LOG"; exit 1; }

echo "=== 最近 $N 筆操作 ==="
grep "^## \[" "$LOG" | tail -"$N"
