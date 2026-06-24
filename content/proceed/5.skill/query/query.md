---
title: Skill — Query（查詢）
tags:
  - 系統/skill
updated: 2026-05-07
---

# Skill：Query 查詢

> 觸發詞：「查詢」、「問」、「分析」、「比較」、「研究 X」

> [!note] 定位
> Query 是把已 ingest 的資料轉成 insight 的流程。`Raw_data` 保存來源，`lib/company・tech・supply_chain` 保存整理後知識，`lib/4.analyze/` 保存可複用的投資判斷、比較結論與觀察框架。

---

## 完整流程

### Step 1：理解問題
拆解涉及的**公司**、**技術**、**供應鏈主題**、**時間範圍**、問題類型（事實 / 比較 / 時程 / 供應鏈 / 投資觀點）。

判斷是否屬於 query：
- ✅ 從既有資料庫回答問題、比較、歸納瓶頸、找先行指標、整理投資觀點
- ✅ 使用者問「現在 X 怎麼看」、「瓶頸在哪」、「誰受惠」、「和 Y 比較」、「這個 thesis 是否成立」
- ❌ 新資料入庫、上傳檔案整理、URL 擷取、PDF 解析 → 走 ingest

### Step 1.5：Wiki-first 找資料原則

Query 找資料必須以 wiki 內容為主，不可直接跳到 web 或模型記憶硬答。

標準順序：
1. **Index first**：先讀 `proceed/2.index/index.md` 總覽，再依問題類型讀對應分檔（`index_company` / `index_tech_supply` / `index_analyze` / `index_raw`），定位相關頁。不需全讀所有分檔。
2. **Lib first**：優先讀 `lib/` 編譯頁，包括 company / tech / supply_chain / analyze / schedule。
3. **Link expansion**：沿著 wikilink、`aliases`、`related_companies`、`related_topics` 擴展相關頁。
4. **Analyze reuse**：若已有相近 `lib/4.analyze/`，優先引用或更新，不重複推理。
5. **Raw only for verification**：只有需要確認原文、數字、日期、claim、矛盾資訊時，才回讀 Raw_data。
6. **Web only for freshness / gaps**：只有使用者問「最新 / 目前 / 最近」、wiki 無答案、或需要外部查證時才用 web_research；web 查到的重要內容若要保存，需走 ingest 或記入 analyze。

### Step 2：定位相關頁面
讀取 `proceed/2.index/index.md` 總覽後，挑相關索引分檔找頁面。
確認 `lib/4.analyze/` 是否已有相同問題的分析（查 `index_analyze.md`）。

定位順序：
1. index 分檔：先找相關 company / tech / supply_chain / analyze
2. `aliases`：若問題是細項術語（如 FBG、EML、ELSFP），先查技術頁 aliases 對應母頁
3. 既有 analyze：若已有分析頁，先更新或引用，不重複建立同題頁
4. Raw_data：只在需要原文、數字、日期、矛盾判斷時回源

### Step 3：深入讀取
依相關性排序讀取，優先讀：
1. company / tech / supply_chain 頁
2. 既有 analyze / schedule 頁
3. 只在需要查證數字、來源日期、矛盾資訊或原文脈絡時，回讀引用的 Raw_data 原文段落

Raw_data 只保存來源 metadata 與原始全文，不保存 AI 摘要。一般查詢不要重新讀大量 Raw_data；先讀已編譯的 `lib/` 頁，只有查證或衝突判斷才回源。

### Step 3.5：形成 insight

Query 不只是摘要，需主動抽取可複用 insight：

| Insight 類型 | 例子 | 應記錄欄位 |
|--------------|------|------------|
| 瓶頸排序 | 光通瓶頸：Pump Laser / EML → FBG / Micro Lens → Paddle Card | 排序、原因、受惠環節 |
| 受惠鏈 | 雙鍵受台光電 M8 / M9 導入帶動 | 供應鏈位置、關係、風險 |
| 先行指標 | Fanuc / Yaskawa 訂單、交期、PMI | 指標、領先性、追蹤方式 |
| 比較結論 | 上銀 vs 亞德客誰對復甦更敏感 | 差異、情境、風險 |
| Thesis / 反證 | CPO 轉 ELS 是否改變台廠價值分配 | 核心假設、反證條件 |

若答案包含 EPS、目標價、產能、ASP、交期、量產時程、供需缺口、供應商地位等關鍵投資 claim，需標記：
- 來源 wikilink
- 來源日期
- claim 類型：fact / company_comment / estimate / user_estimate / inference
- 信心水準：高 / 中 / 低

### Step 4：合成答案

| 問題類型 | 適合格式 |
|---------|---------|
| 事實查詢 | 簡答 + 來源引用 |
| 供應鏈 | Obsidian Canvas 圖譜，必要時附 Mermaid 輔助圖 |
| 比較分析 | Markdown 表格 |
| 時程 | Mermaid gantt |
| 複雜分析 | 段落 + 結論 callout |

答案必須附 wikilink 來源：
```markdown
根據 [[報告_XXX]] 和 [[2330_台積電（市）]]...
```

若答案包含 EPS、目標價、產能、量產時程、供應商地位等關鍵 claim，需附來源日期或說明其為券商預估、推論或未確認資訊。

### Step 5：記錄 insight 至 analyze

Query 的重要輸出是 `lib/4.analyze/`。若本次答案具投資價值或未來可複用，需主動詢問：

> 「這個分析有可追蹤的投資觀點，是否要記錄到 `lib/4.analyze/`？」

若使用者明確說「記下來」、「加到資料庫」、「保存這個觀點」、「建立分析頁」，則不需再問，直接建立或更新 analyze 頁。

若是：依 `schema_analyze.md` 建立分析頁，跑 `python3 scripts/gen_index.py` 更新 index，並 `obsidian append` 寫入 `proceed/1.log/log.md`。

#### 何時值得記錄

- 有跨 company / tech / supply_chain 的整合
- 有瓶頸排序、受惠環節、風險與反證
- 有可追蹤指標或時間點
- 是使用者明確表達的重要觀點
- 未來可能反覆查詢

#### 何時不必記錄

- 單純查一個事實或檔案位置
- 只是在確認規則、流程、檔案是否存在
- 資料不足且沒有形成判斷，只需建議後續 ingest

#### Analyze 命名

`lib/4.analyze/分析_[主題][年份或情境].md`

範例：
- `分析_光通訊瓶頸與台廠受惠環節2026.md`
- `分析_雙鍵台光電M9材料鏈2026.md`
- `分析_自動化產業復甦2026.md`

#### Analyze 寫入後 QA

- 更新 `proceed/2.index/index.md`
- 更新 `proceed/1.log/log.md`
- 只檢查本次新增 / 更新頁面的 wikilink 是否可解析
- 不主動跑全庫 lint，除非使用者要求健康檢查

---

## 特殊查詢

- **供應鏈查詢**：讀 `lib/3.supply_chain/` → 優先生成或引用 Obsidian Canvas 圖譜；簡短回答可附 Mermaid 輔助圖
- **時程查詢**：讀 `lib/5.schedule/` → 生成 Mermaid gantt
- **比較查詢**：分別讀兩頁 → 對比表格 + 投資含義
- **找不到答案**：誠實告知，建議 ingest 新資料

---

## Query 與 Ingest 分工

| 任務 | 使用 skill | 是否寫 Raw_data | 是否寫 analyze |
|------|------------|-----------------|----------------|
| 新 PDF / md / URL 入庫 | ingest | 是 | 視內容與使用者確認 |
| 問現有資料庫觀點 | query | 否 | 有 insight 時主動詢問 |
| 比較兩家公司 | query | 否 | 通常值得 |
| 整理產業瓶頸 | query | 否 | 通常值得 |
| 查最新外部資訊 | web_research + query | 只在要保存來源時 | 視結論 |

Query 不應修改 Raw_data；若 query 發現 Raw_data 有錯，應回報並詢問是否走 cleanup / 修正流程。

---

## Web 使用邊界

Query 預設不使用 web。符合以下情況才補 web：
- 使用者明確要求「查最新」、「現在市場」、「最近消息」、「搜尋」
- 問題具有時效性，wiki 內容可能過期
- wiki 缺少關鍵資料，且需要外部查證
- 高風險 claim 需要來源確認

使用 web 後仍要回到 wiki：
- 先用 wiki 框架解讀 web 資料
- 若 web 內容有保存價值，詢問是否 ingest
- 若 web 只補強 query insight，記錄 analyze 時需標明 web 來源與查詢日期
