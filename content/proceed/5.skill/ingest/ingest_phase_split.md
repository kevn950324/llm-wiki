---
title: Skill — Ingest Phase 分段規則（token 優化核心）
tags:
  - 系統/skill
updated: 2026-05-20
---

# Ingest：Phase 分段規則

> 對應 `ingest.md` 規則 #1、#4、#5、#15、#16；本檔是 token 優化的核心。

---

## 三段式總表

| 階段 | 執行者 | 允許 | 禁止 |
|------|-------|-----|-----|
| **Phase 1**：分析 + Raw_data 落地（Steps 0–3）| Claude | 讀檔、bash 查詢、obsidian CLI 小操作；Raw_data 用 `mv` + Edit prepend；**產出要點清單**（不是完整草稿）| Write 全文複製貼上原文 |
| **Phase 2a**：Claude 寫入（Step 4 接續 Edit +（視需要）pilot）| Claude | 接續 Edit、（必要時）pilot Write、obsidian create/append | 在派遣 Codex 後對批次目標檔案做 Write/Edit |
| **Phase 2b**：Codex 批次（Step 4 剩餘 ≥10 頁）| Codex | 照 pilot 樣板與要點清單批次 Write | 自行決定章節/圖片/補資料 |
| **Phase 3**：Claude 收尾（Steps 5–8）| Claude | 雙向連結 append、QA grep、gen_index、log、清 inbox | 大量 Write（已在 Phase 2b 做完） |

---

> [!warning] Codex 獨自執行模式跳過本節
> 若你是 Codex 直接接到「跑 ingest」指令（不是 Claude 派遣的 batch），**下面整段「Codex 派遣門檻」與「派遣後鎖死規則」直接忽略**——你不能派自己，也不需要鎖死自己。
> Codex 獨自執行時：自寫 pilot → 自寫剩餘所有頁 → 自己跑 QA、gen_index、log、清 inbox。

## 🔑 Codex 派遣門檻（2026-05-20 修訂）

**新規則：剩餘新建頁 ≥ 10 頁 且 Codex 額度可用 才派**

```
剩餘新建頁 ≤ 9 頁 → Claude 直接寫完
剩餘新建頁 ≥ 10 頁 → 評估是否派 Codex
```

**為什麼從 ≥3 提高到 ≥10：**

| 成本 | 大約 |
|------|------|
| Codex prompt 打包（pilot 路徑 + 要點清單）| ~3K |
| Agent tool 包裝（codex-companion）| ~3K |
| 等待時間風險（>5 分鐘）| 不可預期 |
| 失敗後 Claude 重做的雙倍成本 | 全部重來 |
| **固定成本** | **~6K + 風險** |
| 直接 Claude Write 1 頁的 marginal | ~2–3K |

損益平衡：6K / 2.5K ≈ 2.4 頁。**加上失敗風險與重做成本，門檻拉到 10 頁才划算**。

**例外：可不派 Codex 直接 Claude 寫到底**
- 剩餘新建頁 < 10
- 剩餘幾乎都是 Edit（不是新建）
- Codex 額度用完
- 使用者明確說「Claude 全寫」

---

## 🔒 派遣後鎖死規則（新增 2026-05-20）

**派遣 Codex 後，到收到 task-notification 完成回報之前**：

```
✅ 允許：QA 準備、log 草稿、gen_index 預跑、Phase 3 工作
❌ 禁止：對 Phase 2b 批次目標檔案做任何 Write / Edit / obsidian create
❌ 禁止：Claude 自行接手寫該批次清單上的檔案
```

**超時處理：**
- Codex > 10 分鐘無回應 → 跑 `ps aux | grep codex` 與 Bash kill agent
- kill 後再用 Claude Write 接手剩餘清單
- 不要「派了 Codex 又自己同時寫」（這次案例：雙倍成本 ~25K）

**為什麼鎖死：**
2026-05-20 德微案例：派 Codex 後 Claude 等不到回報自己又寫了 6 頁，結果 Codex 後到才發現 5 頁已存在被跳過。等於：
- 打包 prompt 浪費 ~8K
- Agent 包裝 ~10K
- Claude 自己 Write × 6 ~18K
- Codex 跑 40K 但只寫 1 頁
- **總浪費約 60K**

---

## 📝 Phase 1 筆記：要點清單（不寫完整草稿）

**舊規則（已廢止）：** Phase 1 結束時筆記必須含「每頁完整草稿」（frontmatter + 章節骨架 + 表格列 + 圖說），讓 Codex 能照抄。

**問題：** 同一份內容在 Phase 1 筆記寫一次、Codex prompt 貼一次、寫入檔案又一次 = 3 倍 token。如果 Codex 沒執行（失敗、超時），這份草稿純浪費。

**新規則（2026-05-20）：** 每頁只寫**要點清單**（< 15 行/頁），Codex 自己讀 schema + pilot 補完。

### 要點清單模板

```
### 頁面 N：lib/2.tech/技術_XXX.md
- 類型：技術頁（schema_tech）
- 核心數據：[3-5 個關鍵數字或事實]
- 關鍵 wikilink：[[公司A]]、[[公司B]]、[[技術_相關]]
- 圖片：（無/Mermaid 流程圖/`![[實際檔名]]`）
- 特殊提醒：[1-2 句容易出錯的地方]
```

### Phase 1 筆記範例（德微 ingest 用要點清單版）

```
### 頁面 1：lib/1.company/TW/3675_德微電子（櫃）.md（pilot Claude 自寫）
- 核心：TVS+IGBT+800V SiC+均熱片 IDM，月14k片良率96%
- 2026 營收≥30 億、GM≥40%，產能利用率 100-120%
- 子公司：亞昕（11月興櫃）、喜可士
- 通路：台達電→NVIDIA AI PC
- 代工客戶：DIOD.US（60% 產能）
- 競爭/轉單：Nexperia 外包、揚傑制裁、瑞薩退出
- 關鍵 wikilink：[[DIOD.US(diodes)]]、[[亞昕科技（未）]]
- Mermaid 架構圖

### 頁面 2：lib/2.tech/技術_TVS保護元件.md
- 類型：技術頁
- 核心：雪崩擊穿箝位、< 1ps 響應、Cj < 0.5 pF（Low ESD）
- AI PC 用量 4-16 倍、Low ESD 成長 3-6 倍
- 關鍵 wikilink：[[3675_德微電子（櫃）]]、[[DIOD.US(diodes)]]、[[技術_IGBT]]
- Mermaid 流程圖（突波 → TVS → 接地）

（其餘頁面類同，每頁 < 15 行）
```

Codex 接到要點 + pilot + schema，自己組裝完整內容。

---

## Phase 1 讀取規則

### 規則 A：Schema 優先，禁讀範例頁

判斷頁面格式時，**只讀 `proceed/4.schema/schema_<type>.md`**。

| 寫頁面類型 | 讀的 schema |
|-----------|-------------|
| 公司頁 | `schema_company.md` |
| 技術頁 | `schema_tech.md` |
| 供應鏈頁 | `schema_supply_chain.md` |
| 分析頁 | `schema_analyze.md` |
| 時程頁 | `schema_schedule.md` |
| Raw_data 頁 | `schema_raw_data.md` |

例外：更新某既有頁的特定段落時讀那一頁。

### 規則 B：來源檔一次完整 Read

trimmed PDF / memo / URL 擷取結果一次完整 Read，禁止用 grep / limit / offset 替代。

**grep 只用於：**
1. 已 Read 後在筆記內回查特定關鍵字位置
2. 既有 lib 頁雙向連結檢查
3. QA grep（連續標點 / 簡轉繁 / 圖片）

詳見 [[feedback-ingest-read-not-grep]]。

---

## 短頁面工具選擇

| 工具 | Hook 影響 | 適用 |
|------|----------|-----|
| `obsidian append` / `property:set` / `create`（短頁，content= 字串）| 無 | 任何階段 |
| `Edit` | 只 diff | Phase 2 改既有頁 |
| `Write` | 整份內容在 assistant message | 必要時的 lib/ 新建長頁 |

| 頁面類型 | 預期長度 | 推薦工具 |
|---------|---------|----------|
| Raw_data 頁（含原文全文）| 50–500 行 | **Bash `mv` + Edit prepend frontmatter**（禁 Write 全文）|
| 從零生成極短 Raw_data | 20–30 行 | `obsidian create` |
| 簡短 analyze 頁 | 30–60 行 | < 50 行用 `obsidian create`，否則 Write |
| 公司頁 | 80–150 行 | Write（無法用 obsidian create 因 \n 拼接易出錯）|
| 技術頁 | 100–200 行 | Write |
| 時程頁 | 30–60 行 | < 50 行用 `obsidian create` |
| 短公司頁（Unlisted 子公司）| 20–40 行 | `obsidian create` |

---

## Pilot 規則（非強制；2026-05-26 鬆綁）

pilot 是**啟發式，不是硬性規定**。判斷準則：**vault 是否已有夠好的同類頁可當樣板。**

| 情況 | 做法 |
|------|------|
| vault 已有同類頁（公司頁、技術頁等大宗頁型）| **免 pilot**：在 Codex prompt 直接指向一個現成同類範例頁（例：公司頁指 `lib/1.company/TW/4749_新應材（櫃）.md`、技術頁指任一 `技術_*.md`）+ schema，整批寫到底 |
| 新內容領域 / 框架需判斷 / 無合適範本 | Claude 親寫 1 篇 pilot 再交批次（如新主題首頁、footwear-vs-半導體 這類需定調者）|

pilot 仍保留的價值（要 pilot 時）：① 格式錯誤可在 1 份內發現；② 從 hook 回傳判斷有無平行進程改檔；③ 作為批次樣板。**但成熟 vault 中第 ③ 點多已由現成頁取代**，這是免 pilot 的主因。

pilot 不一定要「親寫整頁」：也可只給框架要點 + 指向範例頁，把所有新頁交 Codex。

**與 Codex 派遣門檻的關係**：免 pilot 時所有新頁都進 Codex 批次，新建頁計數較完整，≥10 頁門檻更容易達標、Codex 攤提更划算。

**批量 ingest 的單位仍是「每篇來源」**：要 pilot 時每篇各自 pilot 一次；免 pilot 時每篇來源直接指範例頁批寫。

---

## Phase 2 接續模式檢查

跨 session / 跨 agent 接手是常態。

> [!danger] 動筆前先查存在，確定存在才不要起草 Write
> **Phase 2 開始前，對「所有」計畫新建頁一次性 `ls` 確認是否存在；確定不存在才起草整頁 Write 內容。**
> 很多看似「新公司」的頁，其實先前已從別的 memo/報告建過（例：竑騰←中信座談、天虹←玉山、頎邦←TIA memo）。
> **失敗模式（禁止重犯）**：以為是新頁 → 先生成整頁 Write 內容 → Write 被「File has not been read yet」拒絕 → 才發現是既有頁。光被拒草稿就浪費大量 token（2026-05-22 一個 session 內竑騰/天虹/頎邦三次，浪費 ~7-8K）。

```bash
# 1. 看 log 最近幾筆
tail -30 proceed/1.log/log.md

# 2. 對所有預計新建頁一次性查存在（zsh glob 無匹配會報錯，用 for-loop + 2>/dev/null）
for f in 1234_公司A 5678_公司B 技術_主題X; do
  hit=$(ls lib/1.company/TW/${f}* lib/1.company/Unlisted/${f}* "lib/2.tech/${f}.md" 2>/dev/null)
  echo "${f}: ${hit:-<新建>}"
done
```

| 情境 | 處理 |
|------|------|
| 檔案不存在 | 走原本流程，才起草 Write |
| 檔案已存在但本次有新資訊 | **先 Read 一次** + Edit 補差異，禁止先起草 Write、禁止整份覆寫 |
| log 顯示部分檔案已完成 | 跳過已完成，只處理剩下的 |
| 既有檔案有「我沒寫過」的內容（Codex 補的）| 保留，只在自己段落補新資訊 |

---

## 進 Phase 2 前自我檢查

1. Phase 1 來源全讀完？要點清單寫了？
2. `tail proceed/1.log/log.md` 看過接續狀態？
3. **對所有計畫新建頁一次性 `ls` 確認存在性**（for-loop 版，見上）；已存在的標記為 Read+Edit，**未確認存在前不起草任何整頁 Write 內容**？
4. 剩餘新建頁 < 10 嗎？是 → Claude 寫到底，不派 Codex
5. 派 Codex → 即時鎖死，不對批次清單做任何 Write/Edit

---

## 子規則（按需載入）

| 情境 | 文件 |
|------|------|
| 偵測到資料衝突 | `ingest_conflict.md` |
| Phase 2b 移交 Codex 批次寫入 | `ingest_codex_batch.md` |
| Context 即將用盡，緊急移交 | `ingest_handoff.md` |
