---
title: Skill — Lint（健康檢查）
tags:
  - 系統/skill
updated: 2026-05-09
---

# Skill：Lint 健康檢查

> 觸發詞：「lint」、「健康檢查」、「整理 wiki」

**重要：Lint 只診斷，不自動修改。所有修改必須取得使用者許可後才執行。**

預設工作不跑全庫 lint；只在使用者明確要求「lint / 健康檢查 / 整理 wiki」、批次遷移、schema / 標籤規則變更、或疑似全庫規則漂移時執行。一般 ingest / 小更新只檢查本次修改檔案與新增 wikilink。

---

## 自動化檢查（首選）

```bash
python3 scripts/lint.py            # 全部檢查
python3 scripts/lint.py --check tags     # 已停用標籤
python3 scripts/lint.py --check related  # 公司頁缺 related_companies 欄位；空陣列合法
python3 scripts/lint.py --check canvas   # 供應鏈頁缺圖
python3 scripts/lint.py --check stale    # 過期（>180d）
python3 scripts/lint.py --check orphan   # 孤兒頁面
python3 scripts/lint.py --check biref    # 雙向連結缺漏
python3 scripts/lint.py --check dead     # 失聯 wikilink
```

`scripts/lint.py` 是 read-only 診斷工具，輸出 markdown 報告。發現問題後與使用者確認再修正。

---

## 檢查清單（人工補充項目）

### 1. 孤兒頁面
有內容但無 backlink 的頁面 → 建議連結目標
```
❌ 孤兒頁面：[[技術_XXX]] — 建議連結至 [[供應鏈_YYY]]
```

### 2. 矛盾資訊
同一數據在不同頁面不一致（EPS、市佔、產能、日期）
```
⚠️ 矛盾：[[2330_台積電（市）]] 寫 X 萬片，[[報告_XXX]] 寫 Y 萬片
→ 建議保留較新來源，加 [!warning] callout
```

### 3. 可能過期
`updated` > 180 天 或 標記 `期` 的頁面
```
🕐 可能過期：[[1234_公司名（市）]]（最後更新 2025-10-01）
```

### 4. 缺失連結
- 公司頁未連結 `[[供應鏈_XXX]]`
- 技術頁未連結廠商 wikilink
- 供應鏈頁未列出所有廠商
```
🔗 缺失連結：[[1234_公司名（市）]] 無供應鏈連結
```

`related_companies: []` 合法，表示目前沒有明確公司關係或尚未確認；lint 只檢查公司頁是否有此欄位，不要求非空。

### 5. 標籤不一致
對照 `data_base/label_dic/label_dic.md`，找未標準化的標籤
```
🏷️ 標籤問題：[[報告_XXX]] 使用 #AI伺服器 → 建議改 #產業/AI伺服器
```

### 6. 建議新建頁面
被 wikilink 超過 3 次但尚無頁面的主題
```
📄 建議新建：[[1234_公司名（市）]]（被引用 5 次，尚無頁面）
```

### 7. Index 失準
index.md 有遺漏或孤兒條目

---

## 回報格式

```markdown
## Lint 報告 [YYYY-MM-DD]

### 摘要
- 孤兒頁面：N 個
- 矛盾資訊：N 處
- 可能過期：N 頁
- 缺失連結：N 處
- 標籤問題：N 個
- 建議新建：N 頁

---
（各項目展開）

### 建議執行順序
1. 矛盾資訊（影響判斷）
2. 缺失連結（影響查詢品質）
3. 標籤一致性
4. 過期標記

請確認後我再執行修改。
```

---

## 執行修改（取得許可後）

依序執行，每次修改後追加 log：
```
## [YYYY-MM-DD] lint | 定期健康檢查
- 修正連結：N 處
- 標籤修正：N 個
```
