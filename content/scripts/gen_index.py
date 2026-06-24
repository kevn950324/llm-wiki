#!/usr/bin/env python3
"""Auto-generate split index files in proceed/2.index/ from wiki frontmatter.

輸出：
  index.md              總覽（各分區頁數 + 指向分檔；query wiki-first 先讀這份）
  index_company.md      公司（台股 / 國外 / 未上市）
  index_tech_supply.md  技術 / 供應鏈 / 時程
  index_analyze.md      分析
  index_raw.md          Raw_data（報告 / memo / 其他）

Usage: python3 scripts/gen_index.py
"""

import re
from pathlib import Path
from datetime import date

WIKI_ROOT = Path(__file__).parent.parent
LIB_DIR = WIKI_ROOT / "lib"
DATA_DIR = WIKI_ROOT / "data_base"
INDEX_DIR = WIKI_ROOT / "proceed" / "2.index"

# (path, section name, is_company_section, output file stem)
SECTIONS = [
    (LIB_DIR / "1.company/TW",        "公司 — 台股",   True,  "index_company"),
    (LIB_DIR / "1.company/Overseas",  "公司 — 國外",   True,  "index_company"),
    (LIB_DIR / "1.company/Unlisted",  "公司 — 未上市 / 內部單位", True, "index_company"),
    (LIB_DIR / "2.tech",              "技術",          False, "index_tech_supply"),
    (LIB_DIR / "3.supply_chain",      "供應鏈",        False, "index_tech_supply"),
    (LIB_DIR / "5.schedule",          "時程",          False, "index_tech_supply"),
    (LIB_DIR / "4.analyze",           "分析",          False, "index_analyze"),
    (DATA_DIR / "Raw_data/報告",      "Raw — 報告",    False, "index_raw"),
    (DATA_DIR / "Raw_data/memo",      "Raw — Memo",    False, "index_raw"),
    (DATA_DIR / "Raw_data/其他",      "Raw — 其他",    False, "index_raw"),
]


def parse_frontmatter(text):
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}, []
    fm_text = m.group(1)
    fm = {}
    tags = []
    in_tags = False
    for line in fm_text.splitlines():
        if re.match(r'^tags\s*:', line):
            in_tags = True
            continue
        if in_tags:
            tag_m = re.match(r'^\s+-\s+(.+)', line)
            if tag_m:
                tags.append(tag_m.group(1).strip())
                continue
            else:
                in_tags = False
        kv = re.match(r'^(\w+)\s*:\s*"?([^"]*)"?\s*$', line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip()
    return fm, tags


def render_company_table(files):
    lines = ["| 頁面 | Ticker | 主要標籤 | 更新日 |", "|------|--------|---------|--------|"]
    rows = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        fm, tags = parse_frontmatter(content)
        title = fm.get("title", f.stem)
        ticker = fm.get("ticker", "-")
        updated = fm.get("updated", "-")
        tag_str = " ".join(f"`{t}`" for t in tags[:3]) if tags else "-"
        lines.append(f"| [[{title}]] | `{ticker}` | {tag_str} | {updated} |")
        rows += 1
    return lines, rows


def render_default_table(files):
    lines = ["| 頁面 | 主要標籤 | 更新日 |", "|------|---------|--------|"]
    rows = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        fm, tags = parse_frontmatter(content)
        title = fm.get("title", f.stem)
        updated = fm.get("updated", "-")
        tag_str = " ".join(f"`{t}`" for t in tags[:3]) if tags else "-"
        lines.append(f"| [[{title}]] | {tag_str} | {updated} |")
        rows += 1
    return lines, rows


FILE_DESC = {
    "index_company":     "公司頁（台股 / 國外 / 未上市）",
    "index_tech_supply": "技術 / 供應鏈 / 時程頁",
    "index_analyze":     "分析頁",
    "index_raw":         "Raw_data 原始資料",
}


def file_header(stem, today):
    return [
        "---",
        f'title: "{stem}"',
        f"updated: {today}",
        "---",
        "",
        f"# Wiki Index — {FILE_DESC[stem]}",
        "",
        f"> 自動產生於 {today}。**請勿手動編輯。** 執行 `python3 scripts/gen_index.py` 更新。",
        "",
    ]


def main():
    today = date.today().isoformat()
    sub_out = {}        # stem -> lines
    sub_counts = {}     # stem -> [(section_name, n)]

    for dir_path, section_name, is_company, stem in SECTIONS:
        if not dir_path.exists():
            continue
        files = sorted(
            [f for f in dir_path.rglob("*.md") if not f.name.startswith(".")],
            key=lambda f: f.stem,
        )
        if not files:
            continue
        out = sub_out.setdefault(stem, file_header(stem, today))
        out.append(f"## {section_name}")
        out.append("")
        if is_company:
            rows, n = render_company_table(files)
        else:
            rows, n = render_default_table(files)
        out.extend(rows)
        out.append("")
        sub_counts.setdefault(stem, []).append((section_name, n))

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    overview = [
        "---",
        'title: "index"',
        f"updated: {today}",
        "---",
        "",
        "# Wiki Index（總覽）",
        "",
        f"> 自動產生於 {today}。**請勿手動編輯。** 執行 `python3 scripts/gen_index.py` 更新。",
        "> 先依任務挑對應分檔讀取，不需全讀。",
        "",
        "| 分區 | 頁數 | 索引檔 |",
        "|------|------|--------|",
    ]
    for stem in FILE_DESC:
        if stem not in sub_out:
            continue
        n_file = sum(n for _, n in sub_counts[stem])
        total += n_file
        sections = "、".join(f"{name} {n}" for name, n in sub_counts[stem])
        overview.append(f"| {sections} | {n_file} | [[{stem}]] |")
        (INDEX_DIR / f"{stem}.md").write_text("\n".join(sub_out[stem]) + f"\n---\n*共 {n_file} 頁*", encoding="utf-8")

    overview += ["", "---", f"*共 {total} 頁，產生於 {today}*"]
    (INDEX_DIR / "index.md").write_text("\n".join(overview), encoding="utf-8")
    print(f"✓ index 拆檔更新完成（總覽 + {len(sub_out)} 分檔，共 {total} 頁）")


if __name__ == "__main__":
    main()
