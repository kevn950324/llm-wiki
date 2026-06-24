---
title: Skill — 分析報告輸出
tags:
  - 系統/skill
updated: 2026-05-28
---

# Skill：分析報告輸出（output/）

> 把 LLM 分析結論導出為 PDF 報告，同時在 `lib/4.analyze/` 留 markdown 摘要，雙向連結。

---

## 觸發

使用者說以下任一類型訊息時進入此 skill：
- 「做一份 …… 的分析報告」
- 「整理成報告 / 整理成 PDF」
- 「output 一份 ……」
- 「給我一份 …… 的研究 / 報告」
- 「給我一篇 …… 報告 / 研究 / 深度分析」
- 「完整介紹 / 完整分析 / 技術分析介紹」
- 「多一點圖 / 多一點圖說 / 圖文報告 / 方便理解」
- 「放到 output」
- 「可以給人看的版本 / 對外讀者可讀的版本」

> [!important] 判斷原則
> Report 的觸發不以「PDF」兩字為唯一條件。只要使用者要求的是**正式長文、完整報告、圖文解釋、對外可讀、需要 output**，就必須走本 skill。即使使用者只說「給我一篇報告」而沒說 PDF，也視為 report。

純 query（沒明說要報告 / 圖文 / PDF / output）只走 `query` skill，把短結論沉澱到 `lib/4.analyze/`，**不**強制走此 skill。

### Report vs Query 快速判斷

| 使用者語氣 / 關鍵字 | Skill |
|---------------------|-------|
| 「給我一篇報告」、「做一份報告」、「整理成報告」、「深度報告」 | report |
| 「最好多一點圖」、「圖說」、「圖文」、「方便理解」 | report |
| 「PDF」、「output」 | report |
| 「完整介紹所有技術 / 流程 / 優缺點 / 誰在做 / 何時量產」 | report |
| 「幫我比較」、「這代表什麼」、「誰受惠」、「瓶頸是什麼」且未要求正式報告 | query |

---

## 產物（每份報告兩個檔，2026-06-12 起）

| 檔案 | 路徑 | 用途 |
|------|------|------|
| PDF 完整報告 | `output/<檔名>.pdf` | 給人閱讀的本地正式版本 |
| 投資重點 memo | `lib/4.analyze/分析_<主題>.md` | 沉澱投資結論、受惠鏈、驗證指標、風險，供 wiki query 回收 |

生成 PDF 時建議寫入 metadata Title（完整報告標題），方便日後用 PDF 閱讀器或其他工具管理：

```python
# 例：pypdf 寫入標題（HTML→PDF 工具若可直接設 metadata 亦可）
from pypdf import PdfReader, PdfWriter
reader = PdfReader("output/<檔名>.pdf")
writer = PdfWriter(clone_from=reader)
writer.add_metadata({**(reader.metadata or {}), "/Title": "<完整報告標題>"})
with open("output/<檔名>.pdf", "wb") as f:
    writer.write(f)
```

報告日期取自檔名結尾 `_YYYYMMDD`，命名務必帶日期。

HTML 是生成 PDF 的中間步驟，轉完 PDF 後**立即刪除**，不留在 vault。

PDF 與 analyze memo 透過 frontmatter 與 wikilink 互相指。內容不重複——PDF 是定稿全文，markdown 是 wiki 內可被引用的投資重點，不只是 PDF 摘要。

> [!important] 必做
> 只要產出正式 PDF 報告，就必須同步建立或更新 `lib/4.analyze/分析_<主題>.md`。不得只產出 PDF 而沒有 analyze memo。

---

## 命名規則

### PDF 檔名（output/）
- 主題鎖單一公司：`<代號>_<公司名>_<YYYYMMDD>.pdf`
  - 例：`2330_台積電_20260517.pdf`
- 主題為技術 / 產業 / 主題鏈：`<主題>_<YYYYMMDD>.pdf`
  - 例：`Meta-lens_memo_20260517.pdf`、`CPO供應鏈_20260517.pdf`
- **日期必帶**；同主題多次輸出靠日期區隔保留歷史版本
- output/ 只放 PDF，不建 md

### 摘要 md 檔名（lib/4.analyze/）
- 統一格式：`分析_<主題>.md`
- 同主題**只留一份**；新一輪研究**更新**既有檔，不另建
- 例：`分析_被動元件供應鏈比較.md`、`分析_Agentic AI受惠名單與台股映射.md`

---

## 投資重點 memo 結構（建立 / 更新 `lib/4.analyze/分析_<主題>.md`）

```markdown
---
title: 分析_<主題>
date: <YYYY-MM-DD>
report_pdf: "[[<檔名>.pdf]]"
related_companies:
  - "[[<代號>_<公司名>]]"
related_topics:
  - "[[<供應鏈或技術頁>]]"
tags:
  - 來源/分析報告
  - 主題/<分類>
confidence: <高 / 中 / 低>
updated: <YYYY-MM-DD>
---

# 分析_<主題>

## 結論
- 一句話 investment thesis
- 主要受惠 / 受壓環節 / 風險 / 觀察點

## 投資重點 memo

| 重點 | 投資含義 | 相關標的 | 信心 |
|------|----------|----------|------|
| <受惠鏈 / 技術質變 / 催化劑> | <為什麼會影響營收、ASP、毛利或估值> | [[...]] | 高 / 中 / 低 |

## Insight

- 非顯而易見的結論 1：例如「不是顆數增加，而是產品 mix 升級」。
- 非顯而易見的結論 2：例如「直接受惠與間接受惠需分層」。
- 反證條件：哪些數據或事件出現時，thesis 需要下修。

## 依據
- 關鍵數字、催化劑、來源頁（用 `[[來源頁]]` 連回 Raw_data / lib）

## 驗證清單

| 追蹤指標 | 為什麼重要 |
|----------|------------|
| <法說 / 訂單 / 產品料號 / 客戶認證 / 產能> | <驗證 thesis 是否轉成實績> |

## 相關
- 公司：[[...]] [[...]]
- 供應鏈：[[...]]
- 報告原檔：![[<檔名>.pdf]]

## 信心水準與假設
- 高 / 中 / 低 + 主要不確定來源
```

---

## 流程

1. 使用者要求做分析報告 → 確認 scope（哪些公司 / 主題 / 時間範圍 / 信心水準是否要求驗證）
2. 蒐集依據：wiki-first（`lib/` 編譯頁、`Raw_data/` 原文）；缺口用 `web_research` 補
3. 產出 HTML → 用 Chrome headless 轉 PDF → 存到 `output/<檔名>.pdf` → **立即刪除 HTML**
4. PyMuPDF 掃描 PDF，裁除底部路徑（見下方腳本），確認 CLEAN
5. 用 pypdf 把**完整報告標題寫入 PDF metadata Title**（見「產物」章節範例）
6. 建立 / 更新 `lib/4.analyze/分析_<主題>.md`：
   - frontmatter `report_pdf` 指向 output PDF
   - 必含「結論」、「投資重點 memo」、「Insight」、「驗證清單」、「信心水準與假設」
   - 若報告提出個股排序、受惠鏈、風險或反證條件，必須同步寫入，不可只留在 PDF
7. 跑 `python3 scripts/gen_index.py`，在 `proceed/1.log/log.md` 記錄 PDF 路徑與 analyze memo 路徑
8. 通知使用者：`output/<檔名>.pdf`、`lib/4.analyze/分析_<主題>.md` 已完成

---

## HTML-to-PDF 規則（正式報告必用）

正式 PDF 報告一律採 **HTML/CSS → PDF** 工作流。LLM 不直接手刻 PDF binary，也不以 screenshots 拼 PDF。

### HTML 產出要求

- HTML 是中間檔，轉完 PDF 後立即刪除，**不留在 vault**
- HTML 必須是單檔可開啟，必要 CSS 直接內嵌在 `<style>`，避免轉 PDF 時遺失樣式
- 報告內容必須對外部讀者自足，不可依賴 wiki link 才能理解
- **多放圖片 / 圖表（重要）**：報告應圖文並茂，不要整篇純文字。每個主要章節盡量配至少一張圖（自繪 HTML/CSS/SVG 流程圖、表格、結構圖，或 `data_base/attachment/` 既有圖片資產）。
  - 圖片優先序：① 自繪 HTML/CSS/SVG（無版權疑慮、最自足）；② vault 既有本地圖片資產（券商/產業報告擷圖，用相對路徑 `../data_base/attachment/xxx.png`）。不得引用會失效的遠端 hotlink。
  - **嵌入既有圖片前必先用 Read 工具看過該圖**，確認內容與你要下的圖說相符——vault 既有 caption 可能與圖不符（曾發生 _031 標為「比較表」實為截面圖）。每張圖加圖號、圖說與**來源標註**（哪份報告、日期）。
  - 圖片用相對路徑、勿寫死 `file:///Users/...`；轉 PDF 時 Chrome 會把圖烘進 PDF，self-contained 不受影響。
- **技術 / 架構 / 製程解釋要具體**：講「它是什麼、在做什麼」時帶具體尺度與物理動作（µm / mm² / ppm / 深寬比 / 間距等數字、為什麼這樣做），並善用對照（如「頭髮約 70µm」「310×310mm vs 12 吋圓晶圓」）。避免只給抽象名詞，讓不熟領域的讀者也能讀懂。
- 使用 print CSS 控制紙張、邊界、斷頁：

```css
@page {
  size: A4;
  margin: 16mm 14mm 18mm;
}

.page-break {
  break-before: page;
}

h1, h2, h3 {
  break-after: avoid;
}

table, figure, .chart, .card {
  break-inside: avoid;
}
```

### 轉 PDF 優先順序

1. 優先用 headless Chrome / Playwright，因為最接近實際瀏覽器渲染，適合圖表、CSS grid、flex、SVG。
2. 若報告偏純文字、表格，且需要更強 paged media，可改用 WeasyPrint。
3. 不用手動瀏覽器列印當正式流程；必須能用命令重跑。

常用 Chrome 指令：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --no-sandbox \
  --disable-gpu \
  --print-to-pdf="$VAULT/output/<檔名>.pdf" \
  --print-to-pdf-no-header \
  "file://$VAULT/output/<檔名>.html"
```

> **必加 `--print-to-pdf-no-header`**：缺少此 flag，Chrome 會在每頁底部印出 `file:///Users/<username>/...` 的絕對路徑，洩漏本機使用者名稱，且破壞版面。每次轉 PDF 都必須帶此 flag。

> [!warning] 新版 Chrome 可能忽略 `--print-to-pdf-no-header`（2026-06 Chrome 148 實測：仍在頁首印日期/標題、頁尾印 file:// 路徑）。**優先改用 Playwright** `page.pdf(display_header_footer=False)`（預設就無頁首頁尾），最穩。Chrome headless 僅作備援；無論哪種，轉完都必跑下方 PyMuPDF 掃描。

> **HTML 內禁用絕對路徑**：圖片、CSS、JS 一律用相對路徑（如 `../data_base/attachment/xxx.png`），禁止寫死 `file:///Users/...` 或任何含使用者名稱的路徑。

若使用 Playwright，需設定：
- `format: "A4"`
- `printBackground: true`
- `preferCSSPageSize: true`
- `margin` 與 CSS `@page` 一致或由 CSS 控制

### 轉 PDF 後必做：PyMuPDF 掃描並裁除路徑

Chrome headless 無論哪種模式，都會把來源 `file:///Users/...` 路徑印在每頁底部。轉完 PDF 後，**必須**用以下腳本掃描並白塊覆蓋，再存檔：

```python
import fitz
from pathlib import Path

pdf_path = Path("output/<檔名>.pdf")
tmp = pdf_path.with_suffix(".tmp.pdf")
doc = fitz.open(pdf_path)
dirty = False
for page in doc:
    rects = page.search_for("/Users/") + page.search_for("file:///")
    if rects:
        dirty = True
        for r in rects:
            strip = fitz.Rect(0, r.y0 - 2, page.rect.width, r.y1 + 2)
            page.add_redact_annot(strip, fill=(1, 1, 1))
        page.apply_redactions()
if dirty:
    doc.save(str(tmp), deflate=True)
    doc.close()
    tmp.replace(pdf_path)
else:
    doc.close()
```

掃描完後再用同樣方法驗證，確認 `CLEAN` 才算完成。

### PDF 驗證要求

PDF 產出後必須至少檢查：
- PDF 檔案存在且非空
- 頁數合理，沒有空白頁或明顯截斷
- 表格、圖表、標題、頁尾沒有重疊或爆版
- 中文字體正常，不出現方塊字；必要時在 CSS 指定本機可用字體
- **無個人路徑**：用 PyMuPDF 搜尋 `/Users/`，確認所有頁面 CLEAN
- **檔案大小 < 100MB**。一般圖文報告應 1-3MB。

驗證不過時，回修 HTML/CSS 後重新轉 PDF，不只交付第一次輸出的檔案。

> [!danger] PyMuPDF 後製 PDF 的肥大陷阱（2026-06 實測踩雷）
> 若用 PyMuPDF `insert_textbox` 補字（尤其用 CJK `.ttc` 字型如 STHeiti），**不要用 `save(incremental=True)`**，否則每次都可能把整套 CJK 字型嵌進去，讓檔案異常膨脹。**做法**：所有編輯完成後，最後一次用 `doc.subset_fonts()` 再 `doc.save(out, garbage=4, deflate=True, clean=True)`（全量重寫＋子集化＋GC），檔案會縮回合理大小。subset 後務必重新 render 受影響頁，確認補的字仍在。

---

## 與其他 skill 的分工

| Skill | 角色 |
|-------|------|
| `query` | 短結論沉澱，只在 `lib/4.analyze/` 寫 md，**不**出 PDF |
| `report`（本 skill） | 正式產出，PDF + analyze md 雙檔，雙向連結 |
| `ingest` | 處理外部 raw 資料進 `Raw_data/`，不出 output |
| `web_research` | 為 query / report 補缺口的外部搜尋與擷取 |

---

## Output 注意（重要）

本初始化包不包含網站發布流程。放進 `output/` 之前確認：
- 不含內部敏感資料、未公開財務細節
- 不直接複製券商研究報告原文逐字（侵權）— LLM 自行歸納改寫的觀點 OK
- PDF 是給外部讀者獨立閱讀的正式報告：不要只寫 `[[wiki頁]]`、`資料庫內某頁指出`、`詳見公司頁` 這類內部引用。引用 wiki / Raw_data / 公司頁時，必須在 PDF 內直接寫出足夠的背景、數字、結論與投資含義；wikilink 只可留在 `lib/4.analyze/` 摘要頁作內部索引。
- 若正式 PDF 產生新的投資假設、個股觀察名單、供應鏈 mapping 或展後 checklist，必須同步沉澱到對應 `lib/4.analyze/分析_<主題>.md`，讓後續 query 能回收使用；PDF 裡面則用外部讀者可懂的公司名稱、代號、產品與驗證訊號。
- 草稿請放別處（例：`proceed/3.unprocessed_data/inbox/`），定稿再移到 `output/`
- HTML 已在 PDF 轉換完成後刪除，不留在 vault。
