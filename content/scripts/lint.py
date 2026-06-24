#!/usr/bin/env python3
"""lint.py — 全庫健康檢查（read-only diagnostic）

檢測項目：
  1. 公司頁缺 related_companies 欄位（空陣列合法）
  2. 供應鏈頁缺結構圖（無 .canvas 且文字頁無 mermaid）
  3. lib 頁過期（updated > 180 天）
  4. 孤兒頁面（lib 內無人 wikilink 引用）
  5. 雙向連結缺漏（A 提到 B，但 B 沒提到 A）
  6. wikilink 指向不存在的頁面

用法：
  python3 scripts/lint.py                # 全部檢查
  python3 scripts/lint.py --check related   # 只跑指定檢查（related/canvas/stale/orphan/biref/dead）
  python3 scripts/lint.py --fix-backlinks   # 機械修復雙向連結缺漏：在缺漏頁尾「## 相關頁面」區塊補反向連結
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
LIB = VAULT / "lib"
DATA = VAULT / "data_base"
LABEL_DIC = DATA / "label_dic" / "label_dic.md"

STALE_DAYS = 180


def parse_frontmatter(text: str) -> tuple[dict, list[str]]:
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


def md_files(base: Path):
    return [p for p in base.rglob("*.md") if not p.name.startswith(".")]


def extract_wikilinks(text: str) -> set[str]:
    return {m.group(1).strip() for m in re.finditer(r'\[\[([^\]|#]+)(?:\|[^\]]*)?(?:#[^\]]*)?\]\]', text)}


# ---------- Checks ----------

def check_missing_related(report: dict) -> None:
    hits = []
    for f in md_files(LIB / "1.company"):
        text = f.read_text(encoding="utf-8")
        m = re.search(r'^related_companies\s*:\s*(.*)$', text, re.MULTILINE)
        if not m:
            hits.append(f.relative_to(VAULT))
    report["missing_related"] = hits


def check_supply_chain_diagram(report: dict) -> None:
    hits = []
    for f in (LIB / "3.supply_chain").glob("*.md"):
        if ".flowchart" in f.name:
            continue
        canvas = f.with_suffix(".canvas")
        text = f.read_text(encoding="utf-8")
        has_mermaid = "```mermaid" in text
        if not canvas.exists() and not has_mermaid:
            hits.append(f.relative_to(VAULT))
    report["supply_chain_no_diagram"] = hits


def check_stale(report: dict) -> None:
    hits = []
    cutoff = date.today() - timedelta(days=STALE_DAYS)
    for f in md_files(LIB):
        text = f.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        u = fm.get("updated")
        if not u:
            continue
        try:
            d = datetime.strptime(u, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d < cutoff:
            hits.append((f.relative_to(VAULT), u))
    report["stale"] = hits


def check_orphans(report: dict) -> None:
    pages = md_files(LIB)
    titles = {p.stem: p for p in pages}

    referenced = set()
    for f in pages + md_files(DATA / "Raw_data"):
        text = f.read_text(encoding="utf-8")
        for link in extract_wikilinks(text):
            if link in titles and titles[link] != f:
                referenced.add(link)

    hits = []
    for stem, p in titles.items():
        if stem not in referenced:
            hits.append(p.relative_to(VAULT))
    report["orphans"] = hits


def check_biref(report: dict) -> None:
    """Check if A→B exists but B→A is missing (within lib/)."""
    pages = md_files(LIB)
    title_to_path = {p.stem: p for p in pages}
    outgoing = {}
    for p in pages:
        text = p.read_text(encoding="utf-8")
        outgoing[p.stem] = {l for l in extract_wikilinks(text) if l in title_to_path and l != p.stem}

    hits = []
    for src, targets in outgoing.items():
        for tgt in targets:
            if src not in outgoing.get(tgt, set()):
                hits.append((src, tgt))
    report["biref_missing"] = hits


def check_dead_links(report: dict) -> None:
    """wikilink 指向不存在頁面（含 .md / .canvas / 任何 Raw_data/attachment 檔案）。"""
    output_dir = VAULT / "output"
    all_pages = md_files(LIB) + md_files(DATA / "Raw_data")
    titles = set()
    for p in all_pages:
        titles.add(p.stem)
        titles.add(p.name)
    for c in LIB.rglob("*.canvas"):
        titles.add(c.stem)
        titles.add(c.name)
    # Raw_data 下所有檔案（含 PDF）
    for f in (DATA / "Raw_data").rglob("*"):
        if f.is_file():
            titles.add(f.name)
            titles.add(f.stem)
    # output 下正式報告與 wrapper（含 PDF / Markdown）
    if output_dir.exists():
        for f in output_dir.rglob("*"):
            if f.is_file():
                titles.add(f.name)
                titles.add(f.stem)
    # 圖片
    for img in (DATA / "attachment").glob("*"):
        titles.add(img.name)
        titles.add(img.stem)

    hits = []
    for f in all_pages:
        text = f.read_text(encoding="utf-8")
        for link in extract_wikilinks(text):
            # 過濾末尾被 markdown 跳脫的 `\` 或多餘空白
            clean = link.rstrip("\\ ").strip()
            if clean in titles:
                continue
            hits.append((f.relative_to(VAULT), link))
    report["dead_links"] = hits


# ---------- Fix ----------

RELATED_SECTION = "## 相關頁面"


def fix_backlinks() -> None:
    """對每個 biref 缺漏 (src→tgt 有、tgt→src 無)，在 tgt 頁尾「## 相關頁面」區塊補 [[src]]。"""
    report = {}
    check_biref(report)
    hits = report.get("biref_missing", [])
    if not hits:
        print("無雙向連結缺漏，不需修復。")
        return

    title_to_path = {p.stem: p for p in md_files(LIB)}
    to_add = defaultdict(list)  # tgt page -> [src stems to backlink]
    for src, tgt in hits:
        to_add[tgt].append(src)

    for tgt, srcs in sorted(to_add.items()):
        path = title_to_path[tgt]
        text = path.read_text(encoding="utf-8")
        existing = extract_wikilinks(text)
        new_links = sorted(set(srcs) - existing)
        if not new_links:
            continue
        lines = "\n".join(f"- [[{s}]]" for s in new_links)
        if RELATED_SECTION in text:
            idx = text.index(RELATED_SECTION) + len(RELATED_SECTION)
            rest = text[idx:].lstrip("\n")
            text = text[:idx] + "\n\n" + lines + ("\n" + rest if rest else "\n")
        else:
            text = text.rstrip("\n") + f"\n\n{RELATED_SECTION}\n\n{lines}\n"
        path.write_text(text, encoding="utf-8")
        print(f"+{len(new_links):>3} backlinks → {path.relative_to(VAULT)}")

    print(f"\n完成：{len(to_add)} 頁補入反向連結。請重跑 lint 確認歸零。")


# ---------- Output ----------

def render(report: dict) -> str:
    out = ["## Lint 報告 [%s]" % date.today().isoformat(), ""]

    out.append("### 摘要")
    out.append(f"- 公司頁缺 related_companies 欄位：{len(report.get('missing_related', []))} 頁")
    out.append(f"- 供應鏈頁缺圖：{len(report.get('supply_chain_no_diagram', []))} 頁")
    out.append(f"- 過期（>{STALE_DAYS}d）：{len(report.get('stale', []))} 頁")
    out.append(f"- 孤兒頁面：{len(report.get('orphans', []))} 頁")
    out.append(f"- 雙向連結缺漏：{len(report.get('biref_missing', []))} 對")
    out.append(f"- 失聯 wikilink：{len(report.get('dead_links', []))} 處")
    out.append("")

    if report.get("missing_related"):
        out.append("### 公司頁缺 related_companies 欄位")
        for p in report["missing_related"]:
            out.append(f"- {p}")
        out.append("")

    if report.get("supply_chain_no_diagram"):
        out.append("### 供應鏈頁缺結構圖（無 .canvas 且無 mermaid）")
        for p in report["supply_chain_no_diagram"]:
            out.append(f"- {p}")
        out.append("")

    if report.get("stale"):
        out.append(f"### 過期（updated > {STALE_DAYS} 天）")
        for p, u in report["stale"]:
            out.append(f"- {p}（{u}）")
        out.append("")

    if report.get("orphans"):
        out.append("### 孤兒頁面（lib 內無人 wikilink 引用）")
        for p in report["orphans"]:
            out.append(f"- {p}")
        out.append("")

    if report.get("biref_missing"):
        out.append("### 雙向連結缺漏（A→B 有，B→A 無）")
        # 同一對只列一次
        seen = set()
        for a, b in report["biref_missing"]:
            key = tuple(sorted((a, b)))
            if key in seen:
                continue
            seen.add(key)
            out.append(f"- [[{a}]] ↔ [[{b}]]")
        out.append("")

    if report.get("dead_links"):
        out.append("### 失聯 wikilink（指向不存在頁面）")
        for path, link in report["dead_links"]:
            out.append(f"- {path} → [[{link}]]")
        out.append("")

    out.append("---")
    out.append("*lint.py 只診斷不修改。修正前需獲使用者許可。*")
    return "\n".join(out)


CHECKS = {
    "related":  check_missing_related,
    "canvas":   check_supply_chain_diagram,
    "stale":    check_stale,
    "orphan":   check_orphans,
    "biref":    check_biref,
    "dead":     check_dead_links,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", choices=list(CHECKS) + ["all"], default="all",
                    help="選擇單項檢查")
    ap.add_argument("--fix-backlinks", action="store_true",
                    help="機械修復雙向連結缺漏（在缺漏頁尾補「## 相關頁面」反向連結）")
    args = ap.parse_args()

    if args.fix_backlinks:
        fix_backlinks()
        return

    report = {}
    if args.check == "all":
        for fn in CHECKS.values():
            fn(report)
    else:
        CHECKS[args.check](report)

    print(render(report))


if __name__ == "__main__":
    main()
