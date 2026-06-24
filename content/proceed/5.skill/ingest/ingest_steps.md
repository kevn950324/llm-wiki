---
title: Skill — Ingest Step 0-8 詳細流程
tags:
  - 系統/skill
updated: 2026-05-20
---

# Ingest：Step 0-8 詳細流程

> 對應 `ingest.md` Step 索引。只在執行該 Step 時讀本檔。

---

## Step 0：判斷資料類型

```bash
ls proceed/3.unprocessed_data/inbox
```

| 副檔名 / 內容 | 類型 | 目標目錄 |
|-------------|------|---------|
| `.pdf` 券商報告 | 報告 | `data_base/Raw_data/報告/` |
| `.md` Markdown 報告 / memo / 使用者整理 | 依內容判斷；單檔加 metadata，不建副本 | 對應 Raw_data 目錄 |
| `.txt` 純文字報告 | 報告 | `data_base/Raw_data/報告/` |
| 法說 / 參訪等活動紀錄 | Memo／活動 | `data_base/Raw_data/memo/活動/` |
| URL 文章、搜尋研究彙整、影片逐字稿 | Memo／產業研究 | `data_base/Raw_data/memo/產業研究/` |
| 短文字筆記、無法歸類雜項 | 其他 | `data_base/Raw_data/其他/` |

不確定時詢問使用者。

---

## Step 0.5：PDF 預處理（session 外執行，本地）

**觸發**：`unprocessed_data/` 中有 `.pdf`。

**先做原檔保存：**
- 規範化 stem：`報告_券商_公司主題_YYYYMMDD`
- PDF 原檔移入 `data_base/Raw_data/報告/<stem>_original.pdf`（不得壓縮、裁切、OCR 覆寫、插入 metadata、刪頁）
- trimmed Markdown 合併 metadata 後存為 `data_base/Raw_data/報告/<stem>.md`

```bash
python3 scripts/pdf_parse.py                          # 全部
python3 scripts/pdf_parse.py path/to/report.pdf       # 單一
python3 scripts/pdf_trim.py                           # 全部 parsed/*.md
python3 scripts/pdf_trim.py parsed/report.md          # 單一
```

**輸出：**
- `data_base/Raw_data/報告/<stem>_original.pdf`
- `data_base/Raw_data/報告/<stem>.md`（唯一可讀 Raw 副本，唯讀）
- `proceed/3.unprocessed_data/parsed/<stem>.md` / `<stem>.trimmed.md`
- `data_base/attachment/<stem>_<n>.png`

**LLM 讀取：** 一般讀 `.trimmed.md`（省 25–35% token）；需要完整財務時讀 `.md`。

> [!note] 圖片保留
> 製程圖、供應鏈圖、產能圖、EPS 趨勢圖嵌入對應 lib 頁；版面裝飾、封面、logo 已在 pdf_parse 自動過濾。

---

## Step 1：URL 來源 → 擷取

**推薦：** session 外跑 `scripts/clip.sh <url> [主題]`，輸出存入 `inbox/`。

**LLM 直接執行：**
```bash
defuddle parse <url> --md --output proceed/3.unprocessed_data/inbox/web_YYYY-MM-DD_主題.md
```

Web 文章 Raw_data 必須含：原始 URL、`captured_at`、defuddle 全文。**不在 Raw_data 內寫 AI 摘要**。

---

## Step 1.5：Markdown 來源 → 單檔落地

**觸發**：使用者上傳 `.md` 或提供 Markdown / memo 文字。

**標準流程（禁止 Write 全文）：**

```bash
# 1. Bash mv 移檔 + 同時改名為 schema 規範檔名
mv proceed/3.unprocessed_data/inbox/<原檔名>.md \
   data_base/Raw_data/memo/<分類>/memo_<主題>_<說明>_<YYYYMMDD>.md

# 2. Read 全文（一次讀完，禁止 grep 替代）
# 3. 識別實體（→ Step 3）
# 4. 查 lib 既有頁（→ Step 4a）
# 5. 規劃 Phase 1 要點清單（每頁 < 15 行，見 ingest_phase_split.md）
# 6. Edit prepend frontmatter
```

**為什麼 Edit prepend 在步驟 6 而非 2：**
- Frontmatter 的 `related_companies` / `tags` 來自步驟 3-5 的識別結果
- 沒做完識別就 prepend 會導致 frontmatter 不完整

**Raw_data 保持原文**：即使含簡體中文，落地時不動（維持唯讀）。簡轉繁僅在後續寫 `lib/` 時做。

---

## Step 2：建立 Raw_data 頁面

依 `schema_raw_data.md` 格式。

**PDF 報告**：`pdf_trim.py` 已預填 frontmatter 骨架。LLM 用 **Edit** 逐欄填空：
- `source:` → 補券商名
- `date:` → 補報告日 YYYY-MM-DD
- `tags:` → 加 `公司/XXX` 等
- `related_companies: []` → 改成完整 wikilink 清單
- `updated:` → 填當日
- `aliases: []` → 視需要

**非 PDF 來源**：依 Step 1.5 流程（mv + Edit prepend）。

**極短純文字（< 30 行）**：可用 `obsidian create` 直接建立。

---

## Step 3：分析內容，識別實體

讀取資料後識別：
- **公司名稱** → 查是否已有頁面
- **技術詞彙**（CoWoS、TGV、CPO…）→ 查既有技術頁；遇英文縮寫/規格先查母頁 aliases，能歸入就主動補；達到拆頁條件時主動提案
- **圖片 / 圖表** → 技術結構圖、製程流程圖、供應鏈圖、產品規格圖優先保留
- **公司關係**（上下游、客戶、供應商、代工/製造夥伴、競爭）→ 待更新 `related_companies`
- **供應鏈主題**（AWS_Trainium3、CoWoS、光通訊…）→ 標記待更新供應鏈頁
- **日期事件**（法說、出貨、展覽）→ 標記待更新時程頁
- **關鍵 claim**（EPS、目標價、產能、量產時程、供應商地位）→ 標記來源、類型、信心

### ★ 必做：偵測「主動提案」變化（規則 #14）

| 變化類型 | 判斷 | 提出格式 |
|---------|-----|---------|
| 資訊衝突 | 新來源與 lib 矛盾 | ⚠️ 衝突：[舊] vs [新]，建議用 `[!warning]` 並列 |
| 供應鏈關係更新 | 新客戶/失去客戶/新競爭者 | ⚠️ 關係更新：[A]↔[B] 從 [舊] 改為 [新] |
| 財務上修/下修 | EPS、目標價、毛利率明顯調整 | ⚠️ 財務：[指標] 從 [X] 調至 [Y] |
| 量產節奏 | 時程提前/延後 > 1 季 | ⚠️ 節奏：[公司/產品] 從 [舊] 調為 [新] |
| 技術主流路線轉向 | 路線收斂/新路線浮現 | ⚠️ 路線：[原] 轉向 [新]，影響 [相關廠商] |

統一格式：`⚠️ 偵測到 [類型]：[舊] → [新]，來源 [[XXX]]，建議更新 [[頁名]]，確認後執行。`

---

## Step 4：查重，建立或更新 lib/ 頁

### 4a-0. Raw memo 編譯意圖確認

memo 含投資 insight / 格局比較 / 潛力評估 → **主動建立 `lib/4.analyze/` 頁，不等使用者要求**（feedback memory）。

涉及尚未建頁的公司、新產業主題、可追蹤催化劑 → 詢問使用者是否建/更新 lib。

### 4a. 查重

```bash
obsidian vault="stock_llm_wiki" search query="EMC" path="lib/1.company"
obsidian vault="stock_llm_wiki" search query="技術_CoWoS" path="lib/2.tech"
```

查技術詞彙同時查：`title`、`aliases`、正文關鍵詞、`proceed/2.index/index_tech_supply.md`。

**細項詞優先補母頁 aliases，不直接建新技術頁**（如 FBG、EML、CW Laser 等）。達拆頁條件時主動提案，不直接寫入。

### 4b. 新建頁面

> **動筆前必查**：先確認該頁不存在（見 `ingest_phase_split.md`「Phase 2 接續模式檢查」的 for-loop `ls`）。確定不存在才起草整頁 Write；已存在則改走 4c 更新（Read + Edit 補差異），不要先起草整頁內容再被 Write 拒絕。

路徑選擇：
- 台股：`lib/1.company/TW/{代號}_{公司名}（市/櫃/興）.md`
- 國外：`lib/1.company/Overseas/{代號}.{交易所}({英文名小寫}).md`
- 未上市/子公司/CSP 內部：`lib/1.company/Unlisted/{公司名}（未）.md`

新建公司頁不可只留一句描述，至少補：主要產品/服務、應用場景、供應鏈位置、`#環節/*`、已知客戶/上下游、資料來源、schema 章節骨架。

### 4c. 更新現有頁面

用 `obsidian append` 加數據、`obsidian property:set` 改 frontmatter。

### 4c-1. 公司關係更新

揭露上下游/客戶/供應商/代工/競爭關係 → 同步更新：
1. frontmatter `related_companies`
2. 正文「相關公司」或「供應鏈位置」段落

`related_companies` 只放 wikilink；關係說明寫在正文表格。更新既有頁時**只追加缺漏，不覆蓋**。

### 4c-2. 技術內容深度與圖片

新增/更新技術頁不要只寫名詞解釋。補：技術定義、原理/流程、關鍵參數、瓶頸、應用場景、受惠公司、圖片或 Mermaid。

> [!danger] 圖片嵌入為強制步驟（規則 #8）
> PDF ingest 後**技術頁與公司頁都必須實際嵌入圖片**。
> - 技術頁 `## 圖解`：至少 1 張來源圖或 Mermaid 圖
> - 公司頁 `## 圖片 / 架構圖`：至少 1 張說明該公司位置的圖
> - 圖片放 `data_base/attachment/`，用 `![[檔名.png]]` 嵌入
> - 圖說需說明圖與該公司/技術的關聯

### 4d. 供應鏈發現 → 詢問

偵測到完整供應鏈或 ≥5 間供應商時，主動詢問是否建 `供應鏈_XXX` 頁。確認後用 `obsidian-visual-skills:obsidian-canvas-creator` 建：
`lib/3.supply_chain/供應鏈_XXX.md` + `供應鏈_XXX.canvas`

### 4e. 投資催化劑 → 雙寫個股頁 + 時程頁（規則 #11）

放量節點、展覽、技術下線、驗證、規格升級 → **同時更新兩處**：
1. 個股公司頁的「時間軸」表格
2. 跨公司時程頁 `lib/5.schedule/時程_<年度|主題|標的>`

法說/參訪原始紀錄放 `Raw_data/memo/活動/`，此步驟只記**影響股價的催化劑**。

### 4f. 雙向連結（輕量版）

ingest 寫入時，**只處理本次資料明確提到的關係**：
- 公司間明確關係 → `property:set` 補 `related_companies`，正文補「相關公司」
- 報告/技術/供應鏈頁明確點名某公司 → 雙方未互引時用 `append` 補 wikilink

**全庫掃描**由 `python3 scripts/lint.py` 定期執行，不在每次 ingest 跑。

### 4g. 關鍵 Claim 查證

對 EPS、目標價、產能、量產時程、供應商地位的 claim：
- 保留來源頁 wikilink 與來源日期
- 標示 `fact` / `estimate` / `thesis` / `rumor`
- 標示信心：高 / 中 / 低
- 來源衝突 → 依 `proceed/5.skill/source_verify/source_verify.md` 處理

---

## Step 5：建立雙向連結

```bash
obsidian vault="stock_llm_wiki" links path="data_base/Raw_data/報告/報告_XXX.md"
obsidian vault="stock_llm_wiki" links path="lib/1.company/TW/1234_公司名（市）.md"
```

缺少連結用 `obsidian append` 補。

---

## Step 7：寫入日誌

```bash
obsidian vault="stock_llm_wiki" append \
  path="proceed/1.log/log.md" \
  content="\n## [YYYY-MM-DD] ingest | 標題摘要\n- 新增 Raw_data：[[XXX]]\n- 更新：[[YYY]]\n- 摘要：一句話"
```

---

## Step 8：清理本次暫存

確認完成項：
- Raw_data 已保存
- `lib/` 頁面已新增/更新
- `gen_index.py` 已跑
- `log.md` 已追加
- QA 無新增死連結/孤兒

預設：刪除 `inbox/` 與對應 `parsed/` 工作檔。debug 或使用者要求保留 → 移到 `proceed/3.unprocessed_data/archive/<YYYY-MM-DD>_<topic>/`。
