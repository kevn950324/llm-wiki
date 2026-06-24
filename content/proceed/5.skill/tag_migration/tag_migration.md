---
title: Skill — Tag Migration（標籤遷移）
tags:
  - 系統/skill
updated: 2026-05-07
---

# Skill：Tag Migration 標籤遷移

> 觸發詞：「標籤遷移」、「修停用標籤」、「tag migration」

用於把舊標籤遷移到 `data_base/label_dic/label_dic.md` 定義的新分類。此 skill 只規範流程；實際修改需使用者確認。

---

## 前置檢查

```bash
python3 scripts/lint.py --check tags
scripts/label_search.sh <keyword>
```

先讀：
- `data_base/label_dic/label_dic.md`
- `proceed/4.schema/schema_company.md`
- `proceed/4.schema/schema_supply_chain.md`
- `scripts/lint.py` 輸出的停用標籤清單


---

## 執行流程

1. 跑 lint 取得候選頁。
2. 分批列出「檔案 → 舊標籤 → 新標籤」對照表。
3. 等使用者確認。
4. 修改 frontmatter tags，不改正文投資內容。
5. 跑 `python3 scripts/gen_index.py`。
6. 跑 `python3 scripts/lint.py --check tags` 驗證。
7. 追加 log。

---

## 禁忌

- 非 `公司/*` 標籤（`產業/*`、`供應鏈/*`、`環節/*`、`技術/*`）達到建立條件時應**積極主動向使用者提案推薦**；未經使用者同意不得直接建立。
- 不趁標籤遷移重寫公司頁內容。
- 不把公司角色放回 `供應鏈/*`。
