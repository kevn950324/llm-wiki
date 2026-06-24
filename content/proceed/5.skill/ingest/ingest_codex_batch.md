---
title: Skill — Ingest Codex 批次寫入（Phase 2b 常態移交）
tags:
  - 系統/skill
updated: 2026-05-20
---

# Ingest：Phase 2b 常態 Codex 批次寫入

> [!warning] 本檔僅供 Claude 派遣 Codex 時使用
> 若你是 Codex 獨自執行 ingest（不是 Claude 派遣的 batch task），**讀到本檔整份直接忽略**。Codex 獨自執行時不會派自己——你就是寫入者，不需要打包 prompt 給自己。

> 由 `ingest.md` 在 Phase 2a pilot 通過、剩餘新建頁面 ≥ 10 個時引用。常規讀取流程不需要載入本檔。

> 與 `ingest_handoff.md` 的差別：本檔是**常態**移交（目的省 token），`ingest_handoff.md` 是**緊急**移交（Claude token 不足才觸發）。

---

## 觸發條件（2026-05-20 修訂，門檻提高）

**同時滿足才派 Codex：**

1. Phase 1 結束，**要點清單已寫好**（每頁 < 15 行，見 `ingest_phase_split.md`；不是完整草稿）
2. Phase 2a 已完成：接續 Edit 補完、Pilot Write 1 篇已落地且回傳格式正確
3. 該篇來源剩餘待新建頁面 **≥ 10 個**（< 10 由 Claude 直接寫到底，因打包/等待/失敗成本 > Write hook 成本）
4. Codex 額度仍可用

**不派 Codex 的情境（Claude 寫到底）：**
- 剩餘新建頁 < 10
- 剩餘多為 Edit（不是新建）
- Codex 額度耗盡
- 過去 30 分鐘內 Codex 曾失敗或超時

## 🔒 派遣後鎖死規則（必遵守）

派遣後到收到 `task-notification` 之前：

```
✅ 允許：QA 準備、log 草稿、gen_index 預跑、Phase 3 工作
❌ 禁止：對 Phase 2b 批次目標檔案做任何 Write / Edit / obsidian create
❌ 禁止：Claude 自行接手寫該批次清單上的檔案
```

**超時 10 分鐘無回應 → kill 後接手：**
```bash
ps aux | grep -i codex  # 找 PID
# Bash 用 kill 或透過 Agent stop
```

**為什麼鎖死：** 2026-05-20 德微案例，派遣後 Claude 同時自己寫，導致雙倍成本約 60K token 浪費。

---

## 移交流程

### Step 1：確認 Pilot 落地與筆記完整度

在組裝 prompt 前先確認：

```bash
# 確認 pilot 檔案已落地
ls lib/1.company/TW/<pilot_stem>.md  # 或 lib/2.tech/<pilot_stem>.md

# 確認本次預計新建的所有檔案路徑都不存在（避免漏掉接續模式）
ls lib/1.company/TW/<剩餘檔案>* lib/2.tech/技術_<剩餘主題>* 2>/dev/null
```

若有檔案已存在 → 移到 Phase 2a Edit 處理，不放進 Codex 批次清單。

### Step 2：組裝 Codex prompt（精簡版）

用 `codex:rescue` skill 派遣，prompt 必須包含以下五區塊：

```
## Phase 2b 批次寫入（混合模式 Codex 批次）

### 入口指引
先讀 proceed/5.skill/codex_write/codex_write.md。
讀 proceed/4.schema/schema_<type>.md 對應每頁類型，照 schema 寫。

### Vault 路徑
<VAULT_ROOT>

### Pilot 樣板（Phase 2a 已落地，Read 它取得格式參照）
- <pilot 完整路徑>，例如 lib/1.company/TW/6937_天虹（市）.md

### Phase 1 要點清單（每頁 < 15 行，Codex 照 schema 補完）
（直接貼上 Claude Phase 1 要點清單；Codex 自己讀 schema + pilot 補完所有章節）

### 來源檔（**只在要點清單不足時才 Read，且需在 log 標註已補讀**）
- data_base/Raw_data/memo/活動/memo_XXX.md
- 預設：Codex 只照 Phase 1 要點清單 + pilot + schema 寫，**不主動讀來源**
- 例外：要點清單缺關鍵欄位 → 才 Read 來源補完，並在最終回報註明補讀了哪幾個欄位

### 待 Codex 寫入清單（依序）
1. lib/1.company/TW/<檔案A>.md — <一行內容摘要>
2. lib/2.tech/技術_<主題>.md — <一行內容摘要>
...

### 不在本批次的工作（Claude Phase 3 做，Codex 不做）
- 雙向連結 obsidian append
- QA grep
- python3 scripts/gen_index.py
- log.md / 清 inbox
```

**舊版 prompt 與新版差異：**
- 舊：貼完整草稿（每頁 ~80 行 × 6 頁 = ~500 行 ~10K token）
- 新：貼要點清單（每頁 < 15 行 × 6 頁 = ~90 行 ~2K token）+ Codex 自讀 schema
- 省 ~8K/次

### Step 3：等 Codex 回報，進 Phase 3 收尾

Codex 回報完成後：

1. **抽樣驗收**：Read 至少 1 個 Codex 寫入的非 pilot 檔案，確認：
   - Frontmatter 欄位齊全且縮排正確
   - 章節順序與 schema 一致
   - 圖片 wikilink 真的有對應檔案（`ls data_base/attachment/<檔名>` 確認）
   - 圖說有寫，不是「（待補）」
   - 連續標點（，，、、。。）已在 Codex 寫入時避開（Phase 3 還會 grep 一次）
2. **發現問題**：直接用 Edit 修正單檔，不重新派 Codex
3. **進入 Phase 3**：依 ingest.md Steps 5–8 收尾

---

## Codex 自由發揮的紅線

Codex 接到本指令時**不允許**做以下事，違反需 Claude 在驗收時修正：

| 紅線 | 為什麼 |
|------|------|
| 自行補 Phase 1 筆記未提供的章節 / 段落 / 數據 | 來源未經 Claude 驗證的內容會破壞 fact / estimate / thesis 的標記與信心水準 |
| 自行決定圖片 wikilink（從 attachment 目錄挑圖）| 圖片選擇需匹配章節主題，由 Claude 在 Phase 1 決定 |
| 改 Pilot 樣板檔案 | Pilot 是格式基準，動它會讓後續批次失準 |
| 跑 gen_index.py / 寫 log / 刪 inbox | 這些是 Phase 3 Claude 收尾工作，順序錯會混淆狀態 |
| 自行讀 PDF/memo 原始來源補資料 | Codex 不在 Phase 1 思考鏈內，補出的內容缺乏交叉驗證 |
| 對既有檔案做 Edit（接續模式）| 接續 Edit 由 Claude Phase 2a 完成，Codex 看不到原本 session 的判斷脈絡 |

---

## 失敗復原

| 狀況 | 處理 |
|------|------|
| Codex 回報部分檔案未寫入（額度中斷、工具錯誤）| Claude 接手剩餘清單，直接 Write 完成 |
| 抽樣驗收發現格式系統性偏差（多份檔案同類錯誤）| 用 Edit 批次修正；下次 ingest 補強 Phase 1 筆記精度，避免再犯 |
| Codex 偷補了筆記沒有的內容 | Edit 刪除該段，標註為「來源未驗證」於 log |
| 發現該寫的檔案漏了 | Claude 直接補寫；不重新派 Codex（打包成本不划算）|
