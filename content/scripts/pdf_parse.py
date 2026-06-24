#!/usr/bin/env python3
"""
pdf_parse.py — 本地 docling 解析 PDF，輸出 Markdown + 圖片

用法：
  python3 scripts/pdf_parse.py                     # 處理 proceed/3.unprocessed_data/inbox/ 與根目錄下所有 PDF
  python3 scripts/pdf_parse.py path/to/file.pdf    # 單一 PDF（相對或絕對路徑）

輸出：
  PDF 原檔 → data_base/Raw_data/報告/<stem>_original.pdf  （不修改內容；執行前建議先把 PDF 改成規範化 stem）
  Markdown → proceed/3.unprocessed_data/parsed/<stem>.md
  圖片     → data_base/attachment/<stem>_<n>.png  （小於門檻的 logo/頁眉自動略過）
  （圖片在 Markdown 中已替換為 Obsidian wikilink：![[filename.png]]）

後續：
  跑 scripts/pdf_trim.py 後會另存 metadata 待補的 trimmed Markdown 到 data_base/Raw_data/報告/<stem>.md。
"""

import shutil
import io
import re
import sys
from pathlib import Path
from typing import Optional

VAULT = Path(__file__).resolve().parent.parent
UNPROCESSED = VAULT / "proceed" / "3.unprocessed_data"
PARSED = UNPROCESSED / "parsed"
ATTACHMENT = VAULT / "data_base" / "attachment"
RAW_REPORTS = VAULT / "data_base" / "Raw_data" / "報告"

# 圖片過濾門檻（logo / 頁眉 / 頁碼通常遠小於此值）
MIN_WIDTH = 250   # px
MIN_HEIGHT = 90   # px


def _is_meaningful(pil_img) -> bool:
    w, h = pil_img.size
    return w >= MIN_WIDTH and h >= MIN_HEIGHT


def process(pdf_path: Path) -> Path:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    from docling_core.types.doc import PictureItem

    stem = pdf_path.stem
    PARSED.mkdir(parents=True, exist_ok=True)
    ATTACHMENT.mkdir(parents=True, exist_ok=True)
    RAW_REPORTS.mkdir(parents=True, exist_ok=True)

    # ── Preserve original PDF as Raw_data source of truth ────────────────────
    raw_stem = stem if stem.endswith("_original") else f"{stem}_original"
    raw_pdf = RAW_REPORTS / f"{raw_stem}.pdf"
    if raw_pdf.exists():
        print(f"  PDF 原檔已存在，略過：data_base/Raw_data/報告/{raw_pdf.name}")
    else:
        shutil.copy2(pdf_path, raw_pdf)
        print(f"  PDF 原檔 → data_base/Raw_data/報告/{raw_pdf.name}")

    # ── Convert ──────────────────────────────────────────────────────────────
    opts = PdfPipelineOptions()
    opts.generate_picture_images = True
    opts.images_scale = 2.0
    opts.do_table_structure = True

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )
    result = converter.convert(str(pdf_path))
    doc = result.document

    # ── Collect pictures, filter small decorative images ─────────────────────
    # Each slot is either a filename (saved) or None (skipped),
    # positionally aligned with <!-- image --> placeholders in the markdown.
    slots: list[Optional[str]] = []
    n_saved = n_skipped = 0

    for item, _level in doc.iterate_items():
        if not isinstance(item, PictureItem):
            continue
        pil_img = item.get_image(doc)
        if pil_img is None:
            slots.append(None)
            continue

        if not _is_meaningful(pil_img):
            w, h = pil_img.size
            slots.append(None)
            n_skipped += 1
            print(f"  略過圖片：{w}×{h}px（logo/裝飾）")
            continue

        n_saved += 1
        fname = f"{stem}_{n_saved:03d}.png"
        dest = ATTACHMENT / fname
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        dest.write_bytes(buf.getvalue())
        slots.append(fname)
        print(f"  圖片 → data_base/attachment/{fname}  ({len(buf.getvalue())//1024}KB)")

    print(f"  圖片：{n_saved} 張保留，{n_skipped} 張略過")

    # ── Export Markdown (default mode = PLACEHOLDER → <!-- image -->) ────────
    md = doc.export_to_markdown()

    # ── Replace placeholders with wikilinks (or drop if skipped) ─────────────
    slot_iter = iter(slots)

    def sub(m: re.Match) -> str:
        try:
            fname = next(slot_iter)
            return f"\n![[{fname}]]\n" if fname else ""
        except StopIteration:
            return ""

    md = re.sub(r"<!-- image -->", sub, md)

    # ── Save Markdown ─────────────────────────────────────────────────────────
    out_md = PARSED / f"{stem}.md"
    out_md.write_text(md, encoding="utf-8")
    print(f"  Markdown → proceed/3.unprocessed_data/parsed/{stem}.md")
    return out_md


def main() -> None:
    if len(sys.argv) > 1:
        targets = [Path(a) for a in sys.argv[1:]]
    else:
        inbox = UNPROCESSED / "inbox"
        targets = sorted(inbox.glob("*.pdf")) + sorted(UNPROCESSED.glob("*.pdf"))
    if not targets:
        print("沒有找到 PDF。請將 PDF 放入 proceed/3.unprocessed_data/inbox/ 再執行。")
        return
    for pdf in targets:
        if not pdf.exists():
            print(f"找不到檔案：{pdf}")
            continue
        print(f"\n[docling] 解析：{pdf.name}")
        try:
            out = process(pdf)
            print(f"完成 ✓  {out.relative_to(VAULT)}")
        except Exception as e:
            print(f"失敗：{e}")
            raise


if __name__ == "__main__":
    main()
