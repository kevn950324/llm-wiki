#!/usr/bin/env bash
# label_search.sh — 查詢 label_dic 現有標籤，避免 LLM 讀整份 label_dic
# Usage: label_search.sh <keyword>
set -euo pipefail

QUERY="${1:?Usage: label_search.sh <keyword>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WIKI_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIC="$WIKI_ROOT/data_base/label_dic/label_dic.md"

[[ -f "$DIC" ]] || { echo "label_dic.md 不存在：$DIC"; exit 1; }

grep -i "$QUERY" "$DIC" || echo "（無符合標籤）"
