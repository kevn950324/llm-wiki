#!/usr/bin/env bash
# clip.sh — 將 URL 擷取至 unprocessed_data/（在 LLM session 外執行，省 token）
# Usage: clip.sh <url> [topic]
set -euo pipefail

URL="${1:?Usage: clip.sh <url> [topic]}"
TOPIC="${2:-}"
DATE=$(date +%Y-%m-%d)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WIKI_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEST="$WIKI_ROOT/proceed/3.unprocessed_data/inbox"

mkdir -p "$DEST"

if echo "$URL" | grep -qE "(youtube\.com/watch|youtu\.be/)"; then
    FILENAME="${TOPIC:+${TOPIC}_}video_${DATE}"
    if command -v yt-dlp &>/dev/null; then
        yt-dlp --write-auto-sub \
               --sub-lang "zh-Hant,zh-Hans,en" \
               --skip-download \
               --convert-subs srt \
               --output "$DEST/${FILENAME}.%(ext)s" \
               "$URL"
        echo "✓ YouTube 字幕 → $DEST/${FILENAME}.srt"
    else
        echo "⚠ yt-dlp 未安裝 (brew install yt-dlp)，改用 defuddle 取描述"
        defuddle parse "$URL" --md -o "$DEST/${FILENAME}_desc.md"
        echo "✓ YouTube 描述 → $DEST/${FILENAME}_desc.md"
    fi
else
    DOMAIN=$(python3 -c "from urllib.parse import urlparse; print(urlparse('$URL').netloc.lstrip('www.'))" 2>/dev/null || echo "web")
    FILENAME="${TOPIC:+${TOPIC}_}${DOMAIN}_${DATE}"
    defuddle parse "$URL" --md -o "$DEST/${FILENAME}.md"
    echo "✓ 網頁擷取 → $DEST/${FILENAME}.md"
fi
