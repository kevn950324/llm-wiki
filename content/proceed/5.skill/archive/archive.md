---
title: Skill — Archive（暫存清理與可選歸檔）
tags:
  - 系統/skill
updated: 2026-05-07
---

# Skill：Archive 暫存清理與可選歸檔

> 觸發詞：「清理暫存」、「歸檔」、「archive」、「整理 unprocessed」、「parsed 清理」

用於 ingest 完成後清理 `inbox/` 與 `parsed/` 工作檔，避免 agent 把舊檔誤判成新任務。`archive/` 只作為 debug 或使用者要求時的可選保留區。

---

## 目錄定位

```text
proceed/3.unprocessed_data/
├── inbox/       新放入、尚未處理的來源
├── parsed/      PDF / web / video 預處理產生的工作檔與 plan
└── archive/     可選保留區，僅 debug 或使用者要求時使用
```

Raw source 的正式保存位置仍是：

```text
data_base/Raw_data/
```

---

## 清理規則

- `inbox/`：只放尚未 ingest 的新來源。
- `parsed/`：可放 `.md`、`.trimmed.md`、`.plan.md` 等工作檔。
- ingest 完成且驗證通過後，預設清除本次使用的 `inbox/` 與 `parsed/` 工作檔。
- `archive/`：只有 debug、長流程中斷、或使用者要求保留時才使用。
- 原始 PDF / web 全文若已正式寫入 `data_base/Raw_data/`，不得再修改 Raw_data。

---

## 預設流程

1. ingest 完成後確認 Raw_data、lib 更新、index、log 都已落地。
2. 確認 QA 沒有本次新增的死連結或孤兒頁；不需要跑全庫 lint。
3. 刪除本次使用的 `inbox/` 檔案與對應 `parsed/` 工作檔。
4. 在 log 註明「暫存已清理」。

---

## 可選歸檔流程

若需要保留 debug 線索：

1. 建立 `proceed/3.unprocessed_data/archive/<YYYY-MM-DD>_<topic>/`。
2. 將本次使用的 `inbox/` 與 `parsed/` 工作檔移入該目錄。
3. 保留原始檔名，不壓縮、不改內容。
4. 在 log 註明歸檔位置。

---

## 禁忌

- 不刪除 Raw_data。
- 不刪除 `data_base/attachment/` 內仍被 lib 或 Raw_data 引用的圖片。
- 不把 archive 視為來源真相；來源真相是 `data_base/Raw_data/`。
- 不把已完成 parsed 留在 `inbox/`。
