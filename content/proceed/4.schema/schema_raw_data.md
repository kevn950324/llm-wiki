---
title: Schema — Raw_data 格式規範
tags:
  - 系統/schema
updated: 2026-05-09
---

# Schema：Raw_data (data_base/Raw_data/)

> **重要**：Raw_data 只保存來源原檔、metadata 與原始全文。原始內容**不得刪改或摘要化**；AI 摘要、關鍵概念與投資解讀應寫到對應的 tech/company/supply_chain/analyze 頁。
>
> **PDF 原檔規則**：使用者提供的 PDF 原檔是 Raw_data 的來源真相，必須不做任何修改，以規範化檔名 `報告_..._original.pdf` 移入 `data_base/Raw_data/報告/` 保存。不得同時保留原檔名 PDF 與 `_original.pdf` 兩份。
>
> **PDF trimmed 規則**：PDF ingest 後，`data_base/Raw_data/報告/` 只保存一份由原檔解析並 trim 後的 Markdown 文字檔，供後續讀取與引用。metadata / frontmatter 直接寫在這份 trimmed Markdown；不得另建報告摘要 wrapper 頁，也不得保留第二份同內容 trimmed Markdown。
>
> **Markdown 單檔規則**：若來源本身就是 `.md` 或使用者直接提供 Markdown / memo 文字，該 Markdown 檔本身就是原始紀錄。只在同一個檔案補齊 frontmatter metadata，不再另存「原檔」與「memo 副本」兩份相同內容。

---

## 目錄結構

```
data_base/Raw_data/
├── 報告/           券商研究報告（每份 PDF 僅 original PDF + metadata trimmed Markdown）
├── memo/
│   ├── 產業研究/   web文章、搜尋研究彙整、影片逐字稿等研究型內容
│   └── 活動/       法說、參訪等實際活動紀錄
└── 其他/           隨手記、無法歸類的雜項
```

---

## 類型一：報告 (data_base/Raw_data/報告/)

券商/機構研究報告。

### PDF 原檔

若來源是 PDF：

1. 先決定規範化 stem，例如 `報告_券商_公司主題_YYYYMMDD`。
2. 將使用者提供的 `.pdf` 原檔直接移入 `data_base/Raw_data/報告/<stem>_original.pdf`；檔案內容本身不得修改。
3. 跑 `pdf_parse.py` / `pdf_trim.py` 後，只保留一份 trimmed Markdown：`data_base/Raw_data/報告/<stem>.md`。
4. `frontmatter`、`original_file`、`related_companies`、`aliases` 等 metadata 直接寫在 `<stem>.md`；正文放 trim 後原文與必要的 PDF 原檔 wikilink。
5. 不建立 `報告_...md` 摘要 wrapper 再另外連到 trimmed，也不保留 `<原始檔名>.pdf`、`<原始檔名>_trimmed.md` 等重複副本。
6. `proceed/3.unprocessed_data/parsed/` 只作解析工作區；ingest 完成後依 archive 規則清理暫存。圖片輸出放 `data_base/attachment/` 供 lib 頁引用。
7. 後續需要摘要、投資解讀或修正判讀時，只寫入 `lib/` 或分析頁，不回頭修改 PDF 原檔或 Raw_data trimmed 檔。

```yaml
---
title: "報告_摩根士丹利_台積電2026目標價調升"
source: 摩根士丹利
date: 2026-04-15
tags:
  - 來源/券商報告
  - 公司/台積電
original_format: pdf
original_file: "報告_摩根士丹利_台積電2026目標價調升_original.pdf"
related_companies:
  - "[[2330_台積電（市）]]"
---
```

```markdown
# 報告_摩根士丹利_台積電2026目標價調升

PDF 原檔：[[報告_摩根士丹利_台積電2026目標價調升_original.pdf]]

## 原始內容

貼上 trim 後全文；不另建摘要 wrapper。

![[報告圖片.png]]
```

---

### Markdown / 文字報告單檔

若來源是 `.md`、Markdown 文字或純文字報告：

1. 只保留一個 Markdown 檔，直接作為 Raw_data 原始紀錄。
2. 在同一檔案 frontmatter 補齊 `title`、`source`、`date` / `created`、`tags`、`related_companies` / `related_topics` 等必要屬性。
3. 不另建一份「原檔」和一份「memo_*.md」副本；避免內容重複、浪費空間與 token。
4. 正文保留原文；可做基本 Markdown 結構化與錯字修正，但不寫 AI 摘要、投資解讀或改寫結論。
5. 後續需要摘要、投資解讀或修正判讀時，只寫入 `lib/` 或分析頁，不回頭複製一份 Raw_data memo。

```yaml
---
title: "報告_券商_公司主題"
source: 券商或提供者
date: 2026-05-09
tags:
  - 來源/券商報告
  - 公司/公司名
original_format: markdown
related_companies:
  - "[[1234_公司名（市）]]"
---
```

```markdown
# 報告_券商_公司主題

## 原始內容

保留來源 Markdown / 文字內容，不另建副本。
```

---

## 類型二：Memo／產業研究 (data_base/Raw_data/memo/產業研究/)

包含：web 文章（defuddle 擷取）、搜尋研究彙整、影片逐字稿等研究型內容。

```yaml
---
title: "web_JLCPCB_CCL入門指南"          # web_ / research_ / video_ / memo_ 前綴依內容類型
source: JLCPCB
url: "https://..."                        # 有 URL 時填入
date: 2026-05-03
captured_at: 2026-05-03
tags:
  - 來源/網路文章                          # 來源/網路搜尋 / 來源/影片 依實際來源
  - 技術/CCL
related_topics:
  - "[[技術_CCL]]"
---
```

```markdown
# [前綴_來源_主題]

## 原始內容

> [!quote] 原始全文（defuddle 清洗後 / 搜尋摘要 / 逐字稿，不刪改）
> ...
```

影片逐字稿額外欄位：

```yaml
platform: YouTube
channel: "[頻道名稱]"
video_date: YYYY-MM-DD
transcript_source: auto_sub   # auto_sub / manual / defuddle_desc
```

多來源彙整（research_）frontmatter，當一篇 Raw_data 內容彙整多個 URL（例如 Gemini 搜尋 + defuddle 多頁擷取結果）時使用：

```yaml
---
title: "research_[主題]_[YYYY-MM-DD]"
query: "[搜尋關鍵字]"
sources:
  - url: "https://..."
    title: "文章標題"
    captured_at: 2026-05-03
tags:
  - 來源/網路搜尋
related_topics:
  - "[[技術_XXX]]"
updated: 2026-05-03
---
```

人為彙整 memo（`memo_` 前綴）沿用單一來源欄位（`source` / `url` 視情況），重點在 `tags` 與 `related_companies` / `related_topics`，內文同樣只放原始彙整內容，不寫 AI 摘要。

若使用者上傳的來源已是 `.md` 或 Markdown 文字，該 memo 檔本身就是原始紀錄：只在同一檔案補 frontmatter，不另建內容相同的原檔與 memo 副本。

---

## 類型三：Memo／活動 (data_base/Raw_data/memo/活動/)

法說、參訪等實際活動的原始紀錄。

```yaml
---
title: "活動_台積電法說_2026Q1"
type: 法說                    # 法說 / 參訪
company: "[[2330_台積電（市）]]"
date: 2026-04-17
tags:
  - 來源/法說                 # 來源/法說 / 來源/參訪
  - 公司/台積電
---
```

```markdown
## 原始紀錄

> [!quote] 原始紀錄
> 逐字稿或參訪筆記...
```

---

## 類型四：其他 (data_base/Raw_data/其他/)

隨手記、即時筆記、無法歸類的雜項。

```yaml
---
title: "隨手記_2026-05-02_CoWoS雷射供應商"
date: 2026-05-02
tags:
  - 來源/隨手記
  - 技術/CoWoS
---
```

直接貼原始筆記，不加 AI 摘要。

---

## PDF 解析與圖片處理

PDF 報告 ingest 時分成「原檔保存」、「metadata trimmed Markdown」與「解析工作檔」三件事：

- **原檔保存**：PDF 原檔以 `<stem>_original.pdf` 移入 `data_base/Raw_data/報告/`，不得修改內容。
- **metadata trimmed Markdown**：將 trim 後 Markdown 存入 `data_base/Raw_data/報告/<stem>.md`，frontmatter 直接寫在此檔，寫入後唯讀，供後續查閱。
- **解析工作檔**：需要讀取內容時，再用 `python3 scripts/pdf_parse.py` 本地解析（Step 0.5），暫存於 `proceed/3.unprocessed_data/parsed/`。

此雙檔保存規則只適用 PDF。`.md` / Markdown 來源不需建立 trimmed Raw 副本或 memo 副本。

解析輸出：
- 解析後 Markdown 工作檔存入 `proceed/3.unprocessed_data/parsed/`
- trim 後 Markdown 合併 metadata 後存成 `data_base/Raw_data/報告/<stem>.md`
- 圖片自動存入 `data_base/attachment/`，格式為 `<stem>_<n>.png`
- Markdown 中圖片已替換為 Obsidian wikilink：`![[<stem>_<n>.png]]`

Raw_data 頁引用圖片時直接複製 `![[filename.png]]`，無需路徑（Obsidian 全庫搜索）。  
助理解圖片（製程圖、供應鏈圖、產能表等）亦應嵌入對應 lib 頁面。

---

## 注意事項
- 原始內容區塊用 `> [!quote]` 包住
- PDF 原檔：只允許原樣移入 Raw_data，不得修改 PDF 內容
- PDF trimmed Markdown：ingest 後只留一份在 Raw_data，metadata 直接寫在同檔；不得另建摘要 wrapper 或第二份 trimmed
- Markdown 來源：只保留單一 Markdown 檔並補齊 frontmatter；不要另建原檔與 memo 副本
- 有圖片的報告：解析圖片可保留助理解圖片引用，版面裝飾圖可略
- 命名：`類型前綴_來源_主題摘要`（避免過長）
- Raw_data 內容不得刪改；摘要與關鍵概念寫入對應 tech/company/supply_chain/analyze 頁
