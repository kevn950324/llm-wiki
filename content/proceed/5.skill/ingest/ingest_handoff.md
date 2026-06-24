---
title: Skill — Ingest Token 不足與 Codex 移交
tags:
  - 系統/skill
updated: 2026-05-09
---

# Ingest：Token 不足時的優先順序與 Codex 移交

> 由 `ingest.md` 在 context 即將用盡時引用。常規 ingest 流程不需要載入本檔。

## 優先順序（執行到哪停哪）

1. 完成 Raw_data 寫入（最重要）
2. 更新 log（記錄已完成部分）
3. 建立 company/tech 基本頁骨架
4. 詳細內容 / 圖片嵌入 / 供應鏈更新 → 打包給 Codex

## 移交流程

**何時觸發**：察覺 context 即將滿載（回應已很長、剩餘步驟還很多），立即執行以下移交，不要繼續做新步驟。

### Step 1：寫入中繼狀態 log

在 `proceed/1.log/log.md` 追加一筆中繼記錄，標明哪些步驟已完成、哪些待執行：

```bash
obsidian vault="stock_llm_wiki" append \
  path="proceed/1.log/log.md" \
  content="\n## [YYYY-MM-DD] ingest 中繼 | 標題摘要\n- 已完成：Raw_data、公司頁 X/11\n- 待 Codex：公司頁 Y–Z、技術頁、供應鏈頁、QA、gen_index\n- 關鍵 context：報告 stem = XXX"
```

### Step 2：組裝 Codex prompt

用 `codex:rescue` skill 派遣，prompt 必須包含：

```
## 繼續執行 ingest（Claude token 不足，移交 Codex）

### Vault 路徑
<VAULT_ROOT>

### 報告 stem
<stem>（例：2026年台灣半導體特化與耗材展望_福邦投顧研究部202603）

### 已完成步驟
- [x] Raw_data 頁
- [x] 公司頁：XXX、YYY（列出已建的）
- [ ] 公司頁：AAA、BBB（待建）

### 剩餘任務（依序執行）
1. 建立公司頁：<檔案路徑> — <內容摘要>
2. 更新技術頁：<頁面> — append <具體段落>
3. 更新供應鏈頁：<頁面>
4. QA：obsidian unresolved / orphans；grep -rL "!\[\[" 確認圖片
5. python3 scripts/gen_index.py
6. 寫入完整 log
7. 刪除 inbox 暫存

### 格式規則
先讀 `proceed/5.skill/codex_write/codex_write.md`，依其規則執行。
```

### Step 3：通知使用者

向使用者說明已移交給 Codex，工作從哪個步驟繼續，等 Codex 完成後再做驗收。
