---
title: Skill — Codex Write（vault 寫入入口）
tags:
  - 系統/skill
updated: 2026-05-20
---

# Skill：Codex Write

執行任何 vault 寫入前，依序讀取以下文件，再開始執行任務：

1. `AGENTS.md` — 架構、核心禁忌、標籤規則
2. 對應任務的 skill 文件（例如 `proceed/5.skill/ingest/ingest.md`）
3. 對應的 schema 文件（例如 `proceed/4.schema/schema_company.md`）

規則以上述文件為準，本檔不重複定義。

---

## 批次寫入模式（接續 Claude pilot）

當收到的 prompt 含「Phase 1 要點清單 + Phase 2a pilot 樣本」時，屬於混合模式 Phase 2b 批次寫入。執行原則：

1. **以 pilot 為樣板**：先 Read prompt 指定的 pilot 檔案路徑，看實際落地的 frontmatter 縮排、wikilink 寫法、章節順序、圖片嵌入格式
2. **照要點清單 + schema 補完**：2026-05-20 修訂後 Claude 給的是「要點清單」（每頁 < 15 行），不是完整草稿。Codex 自己 Read 對應 schema_*.md，照要點清單的核心數據、wikilink、特殊提醒組裝完整頁面內容
3. **來源檔讀取規則**：
   - 預設：**不主動 Read 原始 PDF/memo**，照要點清單 + pilot + schema 寫
   - 例外：要點清單缺關鍵欄位（例如：清單只說「TVS GM 50%」但章節需要其他財務數字），可 Read 來源補完；補讀後在最終回報註明「補讀了 X 來源、補了 Y 欄位」
   - 嚴禁：補入要點清單未提及、來源也未提及的內容
4. **依清單順序連續打**：所有 Write 連續執行，中間不穿插無關 Read/分析；每篇來源各自 Pilot 已由 Claude 完成
5. **接續模式不接手**：既有檔案的 Edit 由 Claude 在 Phase 2a 處理，Codex 不做「Read 既有檔再 Edit 補差異」這類接續工作
6. **完成後回報**：列出本次寫入的所有檔案路徑、有無補讀來源、有無遇到要點清單矛盾；**不主動跑 QA / gen_index / log**（這些是 Claude 在 Phase 3 做）

格式細節（wikilink、callout、frontmatter 縮排）以 `obsidian:obsidian-markdown` 與 schema 為準，疑慮時優先信 pilot 樣板。

---

## Codex 獨自執行模式（非 Claude 派遣的 batch）

若你不是被 Claude 派來執行批次 Write，而是被使用者**直接交付 ingest 任務**（例如使用者直接跟 Codex 說「ingest inbox 那份 memo」），切換到獨立模式：

1. 讀 `proceed/5.skill/ingest/ingest.md`，留意「執行者模式」表格
2. **整份 `ingest_codex_batch.md` 直接忽略**（你不會派自己）
3. **`ingest_phase_split.md` 內「Codex 派遣門檻」與「派遣後鎖死規則」段落直接忽略**
4. 走完整流程：自寫 pilot → 自寫剩餘所有頁 → 自跑 QA + gen_index + log + 清 inbox
5. 要點清單由你自己 Phase 1 階段產出；既然你是寫入者本人，Phase 1 筆記可極簡（要寫什麼直接寫，不需打包給別人）
