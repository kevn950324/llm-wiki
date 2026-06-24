---
title: Skill — 視覺化規範
tags:
  - 系統/skill
updated: 2026-05-07
---

# Skill：視覺化規範

> 供應鏈、時程、架構圖的工具選擇與顏色規範。

---

## 工具選擇

| 圖表類型 | 工具 | Skill | 輸出格式 |
|---------|------|-------|---------|
| 供應鏈圖譜（節點多） | Obsidian Canvas | `obsidian-visual-skills:obsidian-canvas-creator` | `供應鏈_XXX.canvas` |
| 供應鏈圖（節點少 < 10） | Mermaid `flowchart` | 直接寫 \`\`\`mermaid 區塊 | 嵌入在 `.md` 內 |
| 時程 / Gantt | Mermaid | `obsidian-visual-skills:mermaid-visualizer` | 嵌入在 `.md` 內 |
| 複雜架構圖 | Obsidian Canvas | `obsidian-visual-skills:obsidian-canvas-creator` | `XXX.canvas` |
| 簡單關係圖 | Mermaid（快速） | 直接寫 \`\`\`mermaid 區塊 | 嵌入 |

- **時程頁**：Mermaid gantt 嵌入頁面（省 token，不另開檔案）
- **供應鏈頁**：優先 Canvas（互動性高），簡單線性鏈可用 Mermaid；詳見 `proceed/4.schema/schema_supply_chain.md`
- **Excalidraw**：除非使用者明確要求，或維護既有檔案，否則新圖不使用

---

## 顏色規範（Canvas 與 Mermaid `classDef` 共用）

| 節點類型 | 色碼 |
|---------|------|
| 上游設備 | `#ffc9c9`（淺紅） |
| 製程環節 | `#d0bfff`（淺紫） |
| 外部材料 | `#ffd8a8`（淺橙） |
| 核心廠商 | `#a5d8ff`（淺藍） |
| 終端客戶 | `#fff3bf`（淺黃） |
| HBM / 記憶體 | `#c3fae8`（淺青） |
| 基板 / 材料 | `#b2f2bb`（淺綠） |

## Canvas 連線規範

- 主要供應鏈流向：有向 edge（箭頭）
- 補充關係：無箭頭或加短 label
- 同一關係不建立多條重複連線

## Canvas 最小 JSON 規格

若無法呼叫外部 Canvas skill，直接建立 `.canvas` 時需符合 JSON Canvas 基本結構：

```json
{
  "nodes": [
    {
      "id": "16hexid",
      "type": "text",
      "text": "節點文字",
      "x": 0,
      "y": 0,
      "width": 240,
      "height": 80
    }
  ],
  "edges": [
    {
      "id": "16hexid2",
      "fromNode": "16hexid",
      "toNode": "other16hexid",
      "toEnd": "arrow"
    }
  ]
}
```

- `id` 使用不重複的 16 字元 hex 字串
- `edges[].fromNode` 與 `edges[].toNode` 必須對應既有 node id
- 寫入後用 JSON parser 驗證格式
