# Stock LLM Wiki — 操作手冊 (AGENTS.md)

> 每次對話開始時讀取此檔案。詳細規則均在各 skill / schema 文件，**按需讀取**，不需預先全讀。

---

## 快速導覽

| 任務 | 讀取文件 |
|------|---------|
| 新增資料（ingest） | `proceed/5.skill/ingest/ingest.md` |
| 提問 / 產生 insight（query） | `proceed/5.skill/query/query.md` |
| 分析報告輸出（report） | `proceed/5.skill/report/report.md` |
| 健康檢查（lint） | `proceed/5.skill/lint/lint.md` |
| 網路搜尋 + 擷取 | `proceed/5.skill/web_research/web_research.md` |
| 影片 / YouTube 擷取 | `proceed/5.skill/video_clip/video_clip.md` |
| 視覺化（Canvas / Mermaid） | `proceed/5.skill/visualize/visualize.md` |
| 來源查證（source verify） | `proceed/5.skill/source_verify/source_verify.md` |
| 標籤遷移 | `proceed/5.skill/tag_migration/tag_migration.md` |
| 暫存清理 / 可選歸檔 | `proceed/5.skill/archive/archive.md` |
| 標籤管理 | `data_base/label_dic/label_dic.md` |
| 全庫索引 | `proceed/2.index/index.md`（總覽）→ 依任務讀分檔 `index_company` / `index_tech_supply` / `index_analyze` / `index_raw` |
| 操作日誌（最近幾筆） | `scripts/log_tail.sh [n]` |

---

## 架構

```
lib/
├── 1.company/TW/           台股公司，檔名與 title 同格式：{代號}_{公司名稱}（上市別）
│                           上市別：（市）= TWSE 上市，（櫃）= TPEX 上櫃，（興）= 興櫃，（未）= 未上市
│                           範例：2330_台積電（市）.md，依代號數字由小到大排序
├── 1.company/Overseas/     國外公司，檔名與 title 同格式：{代號}.{交易所}({英文名小寫})
│                           範例：NVDA.US(nvidia).md
├── 1.company/Unlisted/     未上市公司、子公司、CSP 內部單位，格式：{公司名}（未）
├── 2.tech/                 技術知識
├── 3.supply_chain/         供應鏈地圖（具體客戶鏈/平台鏈/主題鏈為主軸，如 AWS_Trainium3/CoWoS/光通訊/低軌衛星）
├── 4.analyze/              問答分析（同主題若另出 PDF 報告，於此頁 frontmatter 加 report_pdf 指向 output/）
└── 5.schedule/             投資催化劑（放量節點、展覽、技術下線）

output/                     LLM 產出的本地正式分析報告 PDF（本初始化包不包含網站發布流程）
                            檔名：{代號}_{公司名}_{YYYYMMDD}.pdf 或 {主題}_{YYYYMMDD}.pdf
                            每份 PDF 對應一份 lib/4.analyze/分析_{主題}.md 雙向連結
                            詳見 proceed/5.skill/report/report.md

data_base/
├── Raw_data/               原始全文 / 原檔（唯讀）
│   ├── 報告/               券商研究報告（每份 PDF 僅 original PDF + metadata trimmed Markdown）
│   ├── memo/
│   │   ├── 產業研究/       web文章、搜尋研究、影片逐字稿
│   │   └── 活動/           法說、參訪
│   └── 其他/               隨手記、雜項
├── attachment/             PDF 解析產生的圖片（docling 輸出，供 lib 頁嵌入）
└── label_dic/              標籤字典

proceed/
├── 1.log/  2.index/  3.unprocessed_data/{inbox,parsed,archive}/  4.schema/
└── 5.skill/  ingest/ query/ lint/ web_research/ video_clip/ visualize/ source_verify/ tag_migration/ archive/

scripts/   clip.sh  search.sh  gen_index.py  log_tail.sh  label_search.sh  pdf_parse.py  pdf_trim.py  lint.py
```

---

## 規則索引

| 規則主題 | 文件 |
|---------|------|
| Agent 分工 / 網路搜尋工具 | 依使用者目前 AI 工具設定；若無 Codex/Claude，照本檔與 skill/schema 執行 |
| 公司頁命名格式 | `proceed/4.schema/schema_company.md` |
| Raw_data 各類型格式 | `proceed/4.schema/schema_raw_data.md` |
| 其他分區格式（tech / supply / analyze / schedule） | `proceed/4.schema/schema_*.md` |
| 雙向連結 / 衝突處理 / 日誌格式 | `proceed/5.skill/ingest/ingest.md` |
| 視覺化工具 / 顏色規範 | `proceed/5.skill/visualize/visualize.md` |
| 分析報告輸出格式 / output 規則 | `proceed/5.skill/report/report.md` |
| 標籤分類體系與使用規則 | `data_base/label_dic/label_dic.md` |
| 本地腳本說明 | `scripts/` 各腳本內有說明 |

---

## Skill 觸發優先級

- **Report 優先於 Query**：使用者要求「給我一篇 / 一份報告」、「整理成報告」、「做深度報告」、「圖文報告」、「多一點圖說」、「PDF」、「output」、「可以給人看的研究」、「完整分析」時，必須讀 `proceed/5.skill/report/report.md`，並按 report skill 產出 `output/*.pdf` 與 `lib/4.analyze/分析_*.md`。即使使用者沒有明講「PDF」，只要語氣是正式長文 / 圖文研究報告，就視為 report。本初始化包不包含網站 publish 流程。
- **Query 只處理短答與 insight**：若使用者只是問觀點、比較、受惠鏈、瓶頸、投資 thesis，且沒有要求正式報告、圖文、PDF 或 output，才走 `proceed/5.skill/query/query.md`。
- **Report 可包含 Query / Web Research / Source Verify**：report 不是跳過 wiki-first；仍先讀 `index.md` 與相關 `lib/` 頁，缺口再用 web_research，關鍵 claim 用 source_verify，但最終交付形式仍以 report skill 為準。

---

## 核心禁忌

- `data_base/Raw_data/` 寫入後唯讀：只能 `create`（新增）與 `read`，禁止 `edit` / `append` / `delete`（PDF 兩檔制、Markdown 單檔落地細則見 `ingest.md` 頂部 danger callout）
- 新標籤（`#公司/*` 除外）須先獲使用者許可；但當主題已形成獨立研究頁、具備獨立原理 / 供應鏈 / 投資觀察，或後續明顯需要反覆查詢時，需**主動推薦**新增對應標籤，並詢問使用者是否建立
- `#供應鏈/*` 只放研究供應鏈主軸（如 `AWS_Trainium3`、`CoWoS`、`光通訊`），不可放公司角色或零件環節
- 公司角色、產品環節、零組件位置放 `#環節/*`（如 `封測`、`檢測`、`交換器`、`PCB材料`、`ODM`）
- 遇到細項術語、產品規格、英文縮寫與同義詞（如 EML、FBG、CW Laser、ELSFP、Paddle Card）時，需主動積極補進對應技術頁 `aliases`，讓後續查詢可穩定導回母頁；不要一開始就建立大量 `#技術/*` 標籤。若主題長大成獨立研究頁，或本次任務已建立獨立技術 / 供應鏈 / 分析頁，需主動推薦拆新 tag，並等使用者同意後才新增到 `data_base/label_dic/label_dic.md`
- 新增或更新公司頁時，若資料揭露上下游、客戶、供應商、製造夥伴、競爭或替代關係，必須補 frontmatter `related_companies`，並在正文「相關公司」或「供應鏈位置」說明關係
- 若沒有明確公司關係或關係尚待查證，`related_companies: []` 合法，不需為了通過 lint 硬填
- 技術頁需寫得比摘要深入，涵蓋原理/流程、關鍵參數、瓶頸、應用、相關公司；公司頁基本資料也需補主要產品、應用、供應鏈位置與資料來源，不要只留一句話
- 來源若有助理解的圖片/圖表，應嵌入處理後頁面並加圖說；沒有圖片時，技術/供應鏈頁至少用 Mermaid 補架構圖、流程圖或時程圖
- EPS、目標價、產能、量產時程、供應商地位等關鍵投資 claim 需保留來源、日期與信心水準；需要查證時讀 `source_verify` 規則
- Query 是 insight 沉澱流程：問瓶頸、比較、受惠鏈、先行指標、投資 thesis 時，必須 wiki-first：先讀 `index.md` 總覽、挑相關索引分檔，再讀 `lib/` 編譯頁，沿 wikilink / aliases / related_* 擴展；若形成可複用觀點，需主動詢問是否記錄到 `lib/4.analyze/`，或在使用者說「記下來 / 加到資料庫」時直接建立分析頁
- Query 不修改 Raw_data；Raw_data 只在查證數字、日期、原文脈絡或矛盾資訊時回讀
- Web Research 只補強 wiki：使用者問最新、wiki 有缺口或需要外部查證時才搜尋；web 重要結果需回到 ingest 或 analyze 沉澱
- 預設只驗證本次修改範圍；全庫 `python3 scripts/lint.py` 僅在使用者要求健康檢查、批次整理或疑似全庫規則漂移時執行
- lint 結果需獲許可才能修改
- 不使用 Excalidraw（除非使用者明確要求）
- vault 已有 git 版控（2026-06-12 起）：每次 ingest / 批次修改收尾時 `git add -A && git commit -m "<動作摘要>"`；派 Codex 批次寫入後，驗收落地改用 `git diff --stat` 一眼確認，不必逐段 grep

---
