---
title: Skill — Web Research（搜尋 + 擷取）
tags:
  - 系統/skill
updated: 2026-05-07
---

# Skill：Web Research（搜尋 + 擷取）

> 整合 Gemini CLI 搜尋與 defuddle 擷取，將網路資料帶入 wiki。
> 適用於：需要查詢最新產業動態、新聞、法規、公司資訊時。

> [!warning] Wiki-first 原則
> Web Research 是 wiki 的補強工具，不是 query 的第一入口。若使用者是在問既有資料庫觀點，應先走 `query`：`index.md` → `lib/` 編譯頁 → wikilink / aliases / related_* 擴展 → 必要時 Raw_data 回源。只有需要最新資訊、wiki 缺口或外部查證時，才使用 web。

---

## 觸發條件

- 使用者說「幫我查 X」、「搜尋 X」、「找一下 X 的資料」
- ingest 過程中需要補充背景資料
- 已有特定 URL 需要擷取全文
- query 問題涉及「最新 / 目前 / 最近」且 wiki 內容可能不足或過期

## 不應觸發條件

- 使用者只是詢問既有 wiki 內容或投資觀點
- 問題可由 `lib/company・tech・supply_chain・analyze` 回答
- 只是需要沿著 wikilink、aliases、related_companies 找資料
- Raw_data 已有來源，只需要回源確認數字或日期

---

## 流程

### 0. 先檢查 wiki 是否已有答案

除非使用者明確要求直接搜尋，否則先做：

1. 讀 `proceed/2.index/index.md` 總覽 + 相關索引分檔
2. 查相關 `lib/` 頁
3. 沿 wikilink / aliases / related_* 擴展
4. 判斷缺口：是「wiki 沒資料」還是「需要最新資料」

只有確認需要外部資料時，才進入 web 搜尋。

### 1. 確認搜尋意圖

與使用者確認：
- 搜尋關鍵字（中 / 英）
- 預期資料類型（新聞 / 法說 / 產業報告 / 公司官網）
- 儲存目的地：暫存 `proceed/3.unprocessed_data/inbox/`、Raw 保存 `data_base/Raw_data/memo/產業研究/`，或直接進 ingest 流程

### 2. 執行搜尋（Gemini CLI）

```bash
gemini "搜尋：[查詢關鍵字]"
```

- 回傳結果含摘要與來源 URL
- 選取最相關的 3–5 筆 URL 進行下一步

### 3. 擷取頁面全文（defuddle）

針對每個 URL：

```bash
defuddle parse <url> --md
```

儲存到暫存：

```bash
defuddle parse <url> --md -o proceed/3.unprocessed_data/inbox/web_[主題]_[YYYY-MM-DD].md
```

### 4. 決定存放位置

| 資料類型 | 存放位置 |
|---------|---------|
| 暫存擷取結果 | `proceed/3.unprocessed_data/inbox/` |
| 單篇網路文章 / 搜尋研究彙整 | `data_base/Raw_data/memo/產業研究/` |
| 影片 / 逐字稿 | `data_base/Raw_data/memo/產業研究/`（改用 video_clip skill） |

### 5. 寫入 Raw_data

依 `schema_raw_data.md` 的 Web 文章格式：

```yaml
---
title: "research_[主題]_[YYYY-MM-DD]"
query: "[搜尋關鍵字]"
sources:
  - url: "https://..."
    title: "文章標題"
    captured_at: 2026-05-03
tags:
  - 來源/網路搜尋
  - [相關標籤]
updated: [日期]
---
```

Raw_data 頁只保存 metadata 與原始全文；AI 摘要、投資解讀與關鍵概念寫入 `lib/` 頁。

### 6. 進入 ingest 流程

擷取完成後，通知使用者確認是否進行標準 ingest（更新 company / tech / supply_chain 頁）。

### 7. 回寫 query / analyze

若 web research 是為了回答 query：
- 先用 wiki 既有架構解讀外部資訊
- 在答案中區分「wiki 既有資料」與「web 新增查證」
- 若形成可複用 insight，詢問是否記錄到 `lib/4.analyze/`
- 若外部資料本身值得保存，詢問是否 ingest 到 Raw_data

---

## 注意事項

- 一次搜尋建議不超過 5 個 URL，避免 token 過量
- defuddle 對 paywall 內容無效，遇到時告知使用者
- 搜尋結果若有明顯廣告 / SEO 農場文章，直接跳過
- 搜尋完成後不自動 ingest，需使用者確認
- 不要用 web 結果取代 wiki；web 只補足新資訊、缺口或查證
