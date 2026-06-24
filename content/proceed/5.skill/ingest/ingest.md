---
title: Skill — Ingest（資料攝取，精簡索引版）
tags:
  - 系統/skill
updated: 2026-05-20
---

# Skill：Ingest 資料攝取

> 觸發詞：「ingest」、「處理資料」、「加入新資料」

> [!danger] Raw_data 唯讀規則
> `data_base/Raw_data/` 內的檔案**寫入後即為唯讀**：允許 `create` / `read`，禁止 `edit` / `append` / `delete`。
> - **PDF**：每份只保留 `<stem>_original.pdf` + `<stem>.md`
> - **Markdown 來源**：單檔落地，補完 frontmatter 即視為原始紀錄
> - 補充摘要 → 寫 `lib/`，不回頭改 Raw_data

> [!info] 執行者模式（很重要）
> 本 skill 可由 Claude 或 Codex 獨立執行。差異：
>
> | 模式 | Phase 2a Pilot | Phase 2b 派遣 Codex | Phase 3 收尾 |
> |------|---------------|---------------------|-------------|
> | **Claude 執行** | （視需要）pilot：有同類頁免寫、無範本才親寫 | 剩餘 ≥10 頁才派 Codex，派後鎖死 | Claude 做 |
> | **Codex 獨自執行** | 自己寫 pilot（自我審查格式）| **跳過派遣段（不能自己派自己）** | Codex 自己做完整收尾 |
>
> Codex 模式下，讀到 `ingest_codex_batch.md` 整份**直接忽略**；讀到 `ingest_phase_split.md` 內「Codex 派遣門檻」與「派遣後鎖死」段落**直接忽略**。其餘流程（讀來源、要點清單、寫入、QA、log、清 inbox）一律執行。

---

## ⚡ 強制規則速覽（必背，每次都會用到）

| # | 規則 | 細節文件 |
|---|------|--------|
| 1 | **三段式**：Phase 1 讀+規劃 → Phase 2a Claude pilot → Phase 2b Codex 批次（剩餘新建頁 **≥ 10** 才派）→ Phase 3 Claude 收尾 | `ingest_phase_split.md` |
| 2 | **Schema 優先**：頁面格式只讀 `schema_*.md`，禁讀範例頁 | `ingest_phase_split.md` |
| 3 | **PDF/memo 一次讀完**：禁止 grep 替代 Read | `ingest_phase_split.md` |
| 4 | **Pilot（非強制）**：vault 已有同類頁 → 免 pilot，Codex prompt 指向現成範例頁批寫；新內容領域 / 無範本才親寫 pilot。其餘 ≥10 頁才派 Codex | `ingest_phase_split.md` |
| 5 | **派 Codex 後 Claude 鎖死**：禁止對批次目標檔案做 Write/Edit，超時 10 分鐘 kill 再接手 | `ingest_phase_split.md` |
| 6 | **接續模式 + 動筆前查存在**：Phase 2 前對所有計畫新建頁一次性 `ls` 確認；**確定不存在才起草 Write**，已存在 → Read + Edit 補差異，禁 Write 覆蓋（勿先起草整頁再被拒，浪費 token）| `ingest_phase_split.md` |
| 7 | **Raw_data 唯讀**：見上方 danger callout | 上方 |
| 8 | **圖片強制嵌入**：公司頁 `## 圖片 / 架構圖`、技術頁 `## 圖解` 必有圖+圖說 | `ingest_steps.md` Step 4c-2 |
| 9 | **QA 四檢**：連續標點 / 簡轉繁（僅 lib）/ 圖片嵌入 / 雙向連結（`lint.py --fix-backlinks` 機械補） | `ingest_qa.md` |
| 10 | **公司標籤單語化**：台灣公司 tag 只留中文版，英文名放 aliases | `ingest_steps.md` Step 6 QA |
| 11 | **雙寫催化劑**：公司頁時間軸 + 跨公司時程頁 | `ingest_steps.md` Step 4e |
| 12 | **公司關係必補**：揭露上下游 → `related_companies` + 正文「相關公司」 | `ingest_steps.md` Step 4c-1 |
| 13 | **衝突保留**：兩份來源矛盾 → `[!warning]` 並列 | `ingest_conflict.md` |
| 14 | **變化主動提案**：衝突 / 供應鏈更新 / 財務上修下修 / 量產節奏 / 路線轉向必須提出 | `ingest_steps.md` Step 3 |
| 15 | **Claude 避免 Write 全文**：Raw_data 用 `mv` + Edit prepend；lib/ 長頁優先 obsidian create | `ingest_phase_split.md` |
| 16 | **Phase 1 筆記只給要點，不寫完整草稿**：避免同份內容寫多次 | `ingest_phase_split.md` |

---

## 📂 資料路徑速查

| 路徑 | 用途 |
|------|------|
| `proceed/3.unprocessed_data/inbox/` | 待 ingest 原檔 |
| `proceed/3.unprocessed_data/parsed/` | pdf_parse / pdf_trim 工作區 |
| `data_base/Raw_data/報告/` | 券商報告（`<stem>_original.pdf` + `<stem>.md`） |
| `data_base/Raw_data/memo/{產業研究,活動}/` | memo / 法說 / 研究彙整 |
| `data_base/Raw_data/其他/` | 隨手記、雜項 |
| `data_base/attachment/` | 圖片附件 |
| `lib/1.company/{TW,Overseas,Unlisted}/` | 公司頁 |
| `lib/2.tech/` | 技術頁 |
| `lib/3.supply_chain/` | 供應鏈頁 + canvas |
| `lib/4.analyze/` | 分析頁 |
| `lib/5.schedule/` | 時程頁 |
| `proceed/1.log/log.md` | ingest 紀錄 |
| `proceed/2.index/` | gen_index.py 自動生成（index.md 總覽 + 4 索引分檔） |
| `proceed/4.schema/schema_*.md` | 各類頁面格式規範 |

---

## 必須先載入的 Skills

`Skill("obsidian:obsidian-markdown")` + `Skill("obsidian:obsidian-cli")` — 必載入。

### 按資料類型條件載入

| 情境 | Skill |
|------|-------|
| `.pdf` | pdf_parse.py / pdf_trim.py（session 外執行） |
| `.md` / Markdown 文字 | 單檔落地，補 frontmatter |
| `.pptx` | `Skill("anthropic:pptx")` |
| URL | `Skill("obsidian:defuddle")` |
| 供應鏈 canvas | `obsidian-visual-skills:obsidian-canvas-creator`（用於生成 canvas）；`obsidian:json-canvas`（驗證 JSON 結構正確性） |

---

## Step 索引（詳細流程見 `ingest_steps.md`）

| Step | 一句話 | 詳細位置 |
|------|--------|---------|
| 0 | 判斷資料類型（PDF/MD/URL/memo）| `ingest_steps.md` Step 0 |
| 0.5 | PDF 預處理（session 外跑 pdf_parse + pdf_trim） | `ingest_steps.md` Step 0.5 |
| 1 | URL 來源擷取（defuddle / clip.sh）| `ingest_steps.md` Step 1 |
| 1.5 | Markdown 單檔落地：`mv` + 識別實體 + `Edit prepend frontmatter` | `ingest_steps.md` Step 1.5 |
| 2 | 建立 Raw_data 頁（依 schema_raw_data）| `ingest_steps.md` Step 2 |
| 3 | 分析內容，識別實體（公司/技術/供應鏈/催化劑/claim/變化） | `ingest_steps.md` Step 3 |
| 4 | 查重，建立或更新 lib/ 頁（公司/技術/供應鏈/分析/時程） | `ingest_steps.md` Step 4 |
| 5 | 建立雙向連結 | `ingest_steps.md` Step 5 |
| 6 | ingest 後 QA（unresolved / orphans / 連續標點 / 簡轉繁 / 圖片 / 雙向連結）| `ingest_qa.md` |
| 6.5 | `python3 scripts/gen_index.py` 重新產生 index（總覽 + 4 分檔） | `ingest_qa.md` 末段 |
| 7 | 寫入 `proceed/1.log/log.md` | `ingest_steps.md` Step 7 |
| 8 | 清理 inbox 暫存 | `ingest_steps.md` Step 8 |

---

## Phase 執行順序（詳見 `ingest_phase_split.md`）

```
Phase 1  Claude  讀來源 + 規劃要點清單（不是完整草稿）
Phase 2a Claude  Edit 補既有頁 +（視需要）pilot（vault 有同類頁可免，改指範例頁）；剩餘 < 10 頁直接 Claude 寫完
Phase 2b Codex   只在剩餘 ≥10 頁且 Codex 額度可用才派；派遣後 Claude 鎖死
Phase 3  Claude  雙向連結 + QA + gen_index + log + 清 inbox + git commit
```

---

## 子文件索引

| 情境 | 文件 |
|------|------|
| Step 0–8 詳細流程 | `ingest_steps.md` |
| Phase 分段規則 + Codex 派遣門檻 + 接續模式 | `ingest_phase_split.md` |
| Step 6 QA 細節 + 簡轉繁對照表 | `ingest_qa.md` |
| 偵測到資料衝突 | `ingest_conflict.md` |
| 常態混合模式 Phase 2b 移交 Codex | `ingest_codex_batch.md` |
| Context 即將用盡，緊急移交 | `ingest_handoff.md` |

> [!tip] 載入策略
> 進來 ingest 只需讀本頁（< 130 行）+ 對應子文件。一般 `.md` ingest 只需讀 `ingest_steps.md` 的 Step 1.5/3/4/7/8 段落 + `ingest_phase_split.md`，可省 ~30–40K token vs 舊版單份 ingest.md。
