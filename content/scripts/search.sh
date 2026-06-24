#!/usr/bin/env bash
# search.sh — ripgrep 搜尋 wiki 全庫，避免 LLM 讀整份 index
# Usage: search.sh <keyword> [--files-only]
set -euo pipefail

QUERY="${1:?Usage: search.sh <keyword> [--files-only]}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WIKI_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MODE="${2:-}"

if [[ "$MODE" == "--files-only" ]]; then
    rg --ignore-case --files-with-matches "$QUERY" "$WIKI_ROOT/lib" --glob "*.md"
else
    rg --ignore-case \
       --heading \
       --line-number \
       --max-count 5 \
       --glob "*.md" \
       "$QUERY" "$WIKI_ROOT/lib"
fi
