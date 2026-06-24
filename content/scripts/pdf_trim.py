#!/usr/bin/env python3
"""
pdf_trim.py — 修剪 docling 輸出的 Markdown，減少 LLM token 消耗

功能：
  1. 砍掉免責聲明段落（Important Disclosures / Disclosure Appendix 及以後全部）
  2. 移除歷史目標價 / 評等記錄段落（Rating History 等）

保留：
  - 分析摘要、投資論點
  - EPS 預估、目標價（最新）
  - 技術分析、市場成長分析（福邦類產業報告亦適用）
  - 財務表格（P&L, balance sheet 等）

用法：
  python3 scripts/pdf_trim.py parsed/report.md       # 輸出 parsed/report.trimmed.md
  python3 scripts/pdf_trim.py                        # 處理 parsed/ 下所有 .md（跳過 .trimmed.md）

Raw_data：
  同步另存一份 trim 後 Markdown 到 data_base/Raw_data/報告/<stem>.md，
  並在開頭預填 frontmatter 骨架（title / original_file 由 stem 推得，
  source / date / related_companies 等由 LLM 後續 Edit 填入）。
  若 Raw_data Markdown 檔已存在則不覆寫，維持 Raw_data 寫入後唯讀。
"""

import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PARSED = VAULT / "proceed" / "3.unprocessed_data" / "parsed"
RAW_REPORTS = VAULT / "data_base" / "Raw_data" / "報告"

# 符合此 pattern 的 heading → 截斷到 EOF（免責聲明起點）
CUT_TO_EOF = [
    # English
    r"important\s+disclosures?",
    r"disclosure\s+appendix",
    r"analyst\s+certification",
    r"additional\s+important\s+disclosures?",
    r"legal\s+disclaimers?",
    r"regulatory\s+disclosures?",
    r"general\s+disclosures?",
    # 中文
    r"免責聲明",
    r"揭露事項",
    r"法律聲明",
    r"投資風險警語",
    r"重要聲明",
]

# 符合此 pattern 的 heading → 只移除該段落（不截斷後續內容）
SECTION_REMOVE = [
    r"(rating\s+and\s+)?price\s+target\s+(and\s+rating\s+)?history",
    r"rating\s+(and\s+price\s+target\s+)?history",
    r"12.month\s+rating",
    r"historical\s+(rating|price)",
    r"target\s+price\s+history\s+table",
]


def _matches(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _heading_level(line: str) -> int:
    m = re.match(r"^(#{1,6})\s", line)
    return len(m.group(1)) if m else 0


def _heading_text(line: str) -> str:
    return re.sub(r"^#{1,6}\s+", "", line).strip()


def build_frontmatter_skeleton(stem: str) -> str:
    """為新建 Raw_data Markdown 預填 frontmatter 骨架。

    title 與 original_file 由 stem 推得；其他欄位留空，由 LLM 後續 Edit 填入。
    每個欄位名稱皆唯一，避免 Edit 時撞到 PDF 內文重複的 H2 標題。
    """
    return (
        "---\n"
        f"title: {stem}\n"
        "source: \n"
        "date: \n"
        "tags:\n"
        "  - 來源/券商報告\n"
        "original_format: pdf\n"
        f"original_file: {stem}_original.pdf\n"
        "related_companies: []\n"
        "updated: \n"
        "aliases: []\n"
        "---\n"
        "\n"
        f"# {stem}\n"
        "\n"
        f"PDF 原檔：[[{stem}_original.pdf]]\n"
        "\n"
        "## 原始內容\n"
        "\n"
    )


def trim(md: str) -> tuple[str, dict]:
    lines = md.splitlines()
    result: list[str] = []
    stats = {"cut_eof_at": None, "sections_removed": []}

    i = 0
    while i < len(lines):
        line = lines[i]
        lvl = _heading_level(line)

        if lvl > 0:
            text = _heading_text(line)

            if _matches(text, CUT_TO_EOF):
                stats["cut_eof_at"] = text
                break  # 截斷到 EOF

            if _matches(text, SECTION_REMOVE):
                stats["sections_removed"].append(text)
                # 跳過此段落，直到下一個同級或更高級的 heading
                i += 1
                while i < len(lines):
                    next_lvl = _heading_level(lines[i])
                    if next_lvl > 0 and next_lvl <= lvl:
                        break
                    i += 1
                continue  # 不把此 heading 加入 result，直接處理下一行

        result.append(line)
        i += 1

    return "\n".join(result).rstrip() + "\n", stats


def process(md_path: Path) -> Path:
    md_path = md_path.resolve()
    md = md_path.read_text(encoding="utf-8")
    original_lines = md.count("\n")

    trimmed, stats = trim(md)
    trimmed_lines = trimmed.count("\n")
    saved = original_lines - trimmed_lines

    out = md_path.with_suffix(".trimmed.md")
    out.write_text(trimmed, encoding="utf-8")

    RAW_REPORTS.mkdir(parents=True, exist_ok=True)
    raw_stem = md_path.stem
    if raw_stem.endswith("_original"):
        raw_stem = raw_stem[: -len("_original")]
    raw_out = RAW_REPORTS / f"{raw_stem}.md"
    if raw_out.exists():
        print(f"  Raw_data Markdown 已存在，略過：{raw_out.relative_to(VAULT)}")
    else:
        raw_out.write_text(build_frontmatter_skeleton(raw_stem) + trimmed, encoding="utf-8")
        print(f"  Raw_data Markdown → {raw_out.relative_to(VAULT)}（已預填 frontmatter 骨架）")

    if stats["cut_eof_at"]:
        print(f"  免責聲明截斷：「{stats['cut_eof_at']}」")
    for s in stats["sections_removed"]:
        print(f"  移除段落：「{s}」")
    print(f"  {original_lines} 行 → {trimmed_lines} 行（省 {saved} 行 / {saved*100//original_lines if original_lines else 0}%）")
    print(f"  輸出 → {out.relative_to(VAULT)}")
    return out


def main() -> None:
    if len(sys.argv) > 1:
        targets = [Path(a) for a in sys.argv[1:]]
    else:
        targets = [p for p in sorted(PARSED.glob("*.md")) if ".trimmed" not in p.name]

    if not targets:
        print("沒有找到 .md 檔案。")
        return

    for path in targets:
        if not path.exists():
            print(f"找不到：{path}")
            continue
        print(f"\n[trim] {path.name}")
        try:
            process(path)
        except Exception as e:
            print(f"失敗：{e}")
            raise


if __name__ == "__main__":
    main()
