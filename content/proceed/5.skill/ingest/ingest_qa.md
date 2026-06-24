---
title: Skill — Ingest QA 檢查 + 簡轉繁對照表
tags:
  - 系統/skill
updated: 2026-05-20
---

# Ingest：Step 6 QA 詳細

> 對應 `ingest.md` 規則 #9、#10；只在 Phase 3 收尾時讀。

---

## QA 範圍

預設**只檢查本次新增/更新的檔案與新增 wikilink**，不跑全庫 lint。

```bash
# 找斷掉的 wikilink
obsidian vault="stock_llm_wiki" unresolved

# 找本次新建但沒人連到的孤兒頁
obsidian vault="stock_llm_wiki" orphans
```

只有以下情況才跑 `python3 scripts/lint.py` 全庫：
- 使用者明確要求 lint / 健康檢查
- 標籤規則、schema、索引腳本有變更
- 批次遷移或大量 rename
- 懷疑全庫漂移

發現本次問題立即修正再繼續。

---

## 本次寫入必做的額外 QA

### 1. 公司頁與技術頁有圖片嵌入

```bash
grep -rL "!\[\[" lib/1.company/TW/   # 列出無圖片的公司頁
grep -rL "!\[\[" lib/2.tech/         # 列出無圖片的技術頁
```

若有缺圖 → 立即補嵌入相關報告圖片（步驟見 ingest_steps Step 4c-2）。

### 2. CLI 生成頁面無多餘標點

```bash
grep -rn "，，\|、、\|。。" lib/1.company/ lib/2.tech/ lib/3.supply_chain/
```

有多餘標點 → 用 Edit 直接刪除，不要 append。

### 3. 簡轉繁掃描（**只掃 lib/**；Raw_data 保留原文不掃）

```bash
grep -rn "硅\|激光\|芯片\|网络\|软件\|数据\|信息\|视频\|文件\|缓存\|节点\|用户\|协议\|计算\|默认\|优化\|集成\|模块\|工艺\|信号\|损耗\|损坏\|显示屏\|光通信\|光模块\|算力芯片\|存储" lib/
```

`lib/` 內有簡體/大陸用語 → 用 Edit 改成台灣繁體。**Raw_data 不動**（維持唯讀與原始紀錄）。**僅 quote callout 引用使用者原話保留原樣**。

### 4. 雙向連結補齊

```bash
python3 scripts/lint.py --check biref
```

本次新增的 wikilink 若 B→A 反向缺漏 → 跑 `python3 scripts/lint.py --fix-backlinks` 機械補齊（在缺漏頁尾「## 相關頁面」區塊補反向連結，不耗 LLM token）。修完重跑 `--check biref` 確認歸零。

---

## 簡轉繁對照表（lib 寫入時必改）

| 大陸用語 | 台灣用語 |
|---------|---------|
| 硅 / 硅光 | 矽 / 矽光 |
| 激光 / 激光器 | 雷射 / 雷射器 |
| 芯片 / 算力芯片 | 晶片 / 算力晶片 |
| 信号 / 光信号 | 訊號 / 光訊號 |
| 信息 | 資訊 |
| 数据 | 資料（但「數據」在台灣也通用，保留）|
| 软件 / 硬件 | 軟體 / 硬體 |
| 服务器 | 伺服器 |
| 网络 / 网卡 | 網路 / 網卡 |
| 工艺 | 製程 |
| 集成 / 集成电路 | 整合 / 積體電路 |
| 模块 / 光模块 | 模組 / 光模組 |
| 损坏 / 损耗 | 損壞 / 損耗（同字義保留）|
| 显示屏 | 顯示器 / 螢幕 |
| 光通信 | 光通訊 |
| 行业 | 產業（中性偏台灣用語）|
| 板块（股市）| 類股 / 族群 |
| 默认 / 优化 | 預設 / 最佳化 |
| 接口 / 内存 | 介面 / 記憶體 |

---

## 公司標籤單語化（規則 #10）

台灣公司 frontmatter `tags` **只保留中文版**（如 `公司/富采`）。英文名（Ennostar、Himax、PlayNitride）放 `aliases`（Obsidian 搜尋會 fuzzy match alias）。

海外公司用其慣用英文標籤（如 `公司/NVIDIA`）。

**避免雙語重複標籤**（不要同時 `公司/富采` + `公司/Ennostar`）。台股在美 ADR（如奇景光電 HIMX.US）仍視為台灣公司，保留中文標籤。

---

## Step 6.5：重新產生 index

```bash
python3 scripts/gen_index.py
```

腳本掃全庫 frontmatter 自動更新 `proceed/2.index/` 下總覽 index.md 與 4 個索引分檔，不需 LLM 手動維護。
