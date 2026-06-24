---
title: Skill — Video Clip（影片擷取）
tags:
  - 系統/skill
updated: 2026-05-07
---

# Skill：Video Clip（影片擷取）

> 從 YouTube 或其他影片平台擷取逐字稿、描述與元資料，儲存至 `data_base/Raw_data/memo/產業研究/`（依 `schema_raw_data.md` 影片逐字稿屬「產業研究」型內容）。

---

## 觸發條件

- 使用者貼上 YouTube URL 或影片連結
- 使用者說「幫我擷取這個影片」、「把這個法說影片存進去」

---

## 工具優先順序

| 工具 | 適用情況 | 指令 |
|------|---------|------|
| `scripts/clip.sh` | 預設流程，輸出到 `proceed/3.unprocessed_data/` | `scripts/clip.sh <url> [topic]` |
| `defuddle` | 快速取得影片描述、標題、頻道等 metadata | `defuddle parse <url> --md` |
| `yt-dlp` | 需要完整自動字幕 / 逐字稿（需另行安裝） | 見下方 |

---

## 流程

### 1. 確認影片資訊

請使用者提供：
- YouTube URL
- 影片語言（中文 / 英文）
- 目的（法說 / 產業介紹 / 公司說明）

### 2a. defuddle 擷取（快速，取 metadata + 描述）

優先使用本地腳本：

```bash
scripts/clip.sh <youtube_url> [topic]
```

腳本會在有 `yt-dlp` 時擷取字幕，否則降級用 defuddle 擷取描述。

手動 fallback：

```bash
defuddle parse <youtube_url> --md
```

適合：頻道說明、影片描述、留言等公開文字內容。
限制：無法取得完整逐字稿。

### 2b. yt-dlp 擷取逐字稿（完整，推薦用於法說 / 重要影片）

安裝：
```bash
pip install yt-dlp
# 或
brew install yt-dlp
```

取自動字幕（中文優先，英文備選）：
```bash
yt-dlp --write-auto-sub --sub-lang "zh-Hant,zh-Hans,en" --skip-download --output "/tmp/%(title)s.%(ext)s" <youtube_url>
```

字幕轉純文字（去時間碼）：
```bash
yt-dlp --write-auto-sub --sub-lang "zh-Hant,zh-Hans,en" --skip-download --convert-subs srt --output "/tmp/%(title)s.%(ext)s" <youtube_url>
```

### 3. 寫入 Raw_data

存入路徑：`data_base/Raw_data/memo/產業研究/video_[頻道]_[主題]_[YYYY-MM-DD].md`

```yaml
---
title: "video_[頻道]_[影片主題]_[YYYY-MM-DD]"
type: video_script            # video_script / video_desc
platform: YouTube
url: "https://www.youtube.com/watch?v=..."
channel: "[頻道名稱]"
video_date: YYYY-MM-DD        # 影片發布日期
captured_at: YYYY-MM-DD
language: zh-Hant             # zh-Hant / zh-Hans / en
transcript_source: auto_sub   # auto_sub / manual / defuddle_desc
tags:
  - 來源/影片
  - 公司/[相關公司]
  - [其他相關標籤]
related_companies:
  - "[[2330_台積電（市）]]"
updated: YYYY-MM-DD
---

## 影片資訊

| 欄位 | 內容 |
|------|------|
| 頻道 | |
| 發布日 | |
| 影片長度 | |
| 主題摘要 | |

## 逐字稿 / 描述

> [!quote] 原始內容（保留原文，不刪改）
> ...
```

### 4. 進入 ingest 流程

擷取完成後通知使用者，確認是否進行標準 ingest（更新 company / tech / supply_chain 頁）。

---

## 注意事項

- 優先使用 `yt-dlp` 取完整字幕；`defuddle` 只作備用（取描述）
- 法說 / 公司說明會的影片，字幕準確度可能不足，需使用者校閱
- 字幕語言選擇：繁中 → 簡中 → 英文，無字幕時改用 defuddle 取描述
- 影片超過 2 小時，建議分段記錄重點而非整份逐字稿
- 私人 / 會員限定影片無法擷取，告知使用者
