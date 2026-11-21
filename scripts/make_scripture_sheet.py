#!/usr/bin/env python3
"""
Printable Pulpit Scripture Reference Sheet Generator for Kyle Morrow.

Generates a clean, large-print, pulpit-ready HTML sheet (print straight to paper
or Save as PDF from any browser) with:
  - Opening public reading in KJV (clearly badged; congregation stands)
  - All body Scripture references in NIV in exact preaching order, with movement cues

Two modes:
  1. Extract a structured Scripture sheet skeleton from any sermon manuscript:
       python3 scripts/make_scripture_sheet.py --from-manuscript draft.md --out scripture-refs.md

  2. Render a structured scripture-refs.md (see templates/SCRIPTURE_SHEET.md) to printable HTML:
       python3 scripts/make_scripture_sheet.py scripture-refs.md --out pulpit-scriptures.html

  You can also go straight from a manuscript to a quick-reference HTML index card:
       python3 scripts/make_scripture_sheet.py --from-manuscript draft.md --html pulpit-index.html
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

BIBLE_BOOKS = [
    "Song of Solomon", "Song of Songs",
    "1 Chronicles", "2 Chronicles", "1 Corinthians", "2 Corinthians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John",
    "First Chronicles", "Second Chronicles", "First Corinthians", "Second Corinthians",
    "First Thessalonians", "Second Thessalonians", "First Timothy", "Second Timothy",
    "First Samuel", "Second Samuel", "First Kings", "Second Kings",
    "First Peter", "Second Peter", "First John", "Second John", "Third John",
    "Deuteronomy", "Ecclesiastes", "Lamentations", "Philippians", "Colossians",
    "Revelation", "Genesis", "Exodus", "Leviticus", "Numbers", "Joshua", "Judges",
    "Nehemiah", "Esther", "Psalms", "Psalm", "Proverbs", "Isaiah", "Jeremiah",
    "Ezekiel", "Daniel", "Obadiah", "Habakkuk", "Zephaniah", "Haggai", "Zechariah",
    "Malachi", "Matthew", "Romans", "Galatians", "Ephesians", "Philemon", "Hebrews",
    "Hosea", "Joel", "Amos", "Jonah", "Micah", "Nahum", "Ruth", "Ezra", "Job",
    "Mark", "Luke", "John", "Acts", "Titus", "James", "Jude",
    "1 Chr", "2 Chr", "1 Cor", "2 Cor", "1 Thess", "2 Thess", "1 Tim", "2 Tim",
    "1 Sam", "2 Sam", "1 Kgs", "2 Kgs", "1 Pet", "2 Pet", "1 Jn", "2 Jn", "3 Jn",
    "Gen", "Exod", "Ex", "Lev", "Num", "Deut", "Josh", "Judg", "Neh", "Esth",
    "Ps", "Prov", "Eccl", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Obad",
    "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal", "Matt", "Mk", "Lk", "Jn",
    "Rom", "Gal", "Eph", "Phil", "Col", "Phlm", "Heb", "Jas", "Rev",
]

BOOK_GROUP = "|".join(re.escape(b) for b in BIBLE_BOOKS)
SCRIPTURE_RE = re.compile(
    rf"\b(?:{BOOK_GROUP})\.?\s+(?:chapter\s+)?\d+(?::\d+(?:\s*[-–—]\s*\d+(?::\d+)?)?(?:,\s*\d+(?:\s*[-–—]\s*\d+)?)*|\s*[-–—]\s*\d+(?::\d+)?)?\b",
    re.IGNORECASE,
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    meta: dict[str, str] = {}
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                for fm_line in lines[1:idx]:
                    if ":" in fm_line:
                        k, v = fm_line.split(":", 1)
                        meta[k.strip().lower()] = v.strip().strip('"').strip("'")
                return meta, "\n".join(lines[idx + 1 :])
    return meta, text


def extract_from_manuscript(path: Path) -> tuple[dict[str, str], list[dict], list[dict]]:
    """Extract ordered Scripture references from a sermon manuscript."""
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)

    # Best-effort title detection if not in frontmatter
    if "title" not in meta:
        for line in body.splitlines()[:15]:
            s = line.strip().strip("*#_ ")
            if s and len(s) < 90 and not s.startswith("["):
                meta["title"] = s
                break
        meta.setdefault("title", path.stem.replace("-", " ").title())

    meta.setdefault("church", "Straight Creek Church of God")
    meta.setdefault("preacher", "Kyle Morrow")

    current_heading = "Opening"
    found: list[tuple[str, str, str]] = []  # (ref, heading, context_line)
    seen: set[str] = set()

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            current_heading = re.sub(r"^#+\s*", "", stripped).strip("*_ ")
            continue
        bold_hdr = re.match(r"^\*\*([IVX]+\.\s+[^*]+|[A-Z0-9][A-Z0-9\s:.'’\-–—]+)\*\*$", stripped)
        if bold_hdr and len(bold_hdr.group(1)) <= 80:
            current_heading = bold_hdr.group(1).strip()
            continue
        for m in SCRIPTURE_RE.finditer(line):
            ref = " ".join(m.group(0).split())
            nums = re.findall(r"\d+", ref)
            if nums and int(nums[0]) > 150:
                continue
            key = ref.lower().replace("chapter ", "")
            if key not in seen:
                seen.add(key)
                found.append((ref, current_heading, stripped))

    opening_ref = meta.get("opening_ref")
    opening_entries: list[dict] = []
    body_entries: list[dict] = []

    if opening_ref:
        opening_entries.append({
            "ref": opening_ref,
            "translation": "KJV",
            "cue": "Stand for the reading of the Word",
            "note": "",
            "text": "[VERIFY & PASTE VERBATIM KJV TEXT HERE]",
        })
        for ref, heading, _ in found:
            if ref.lower() == opening_ref.lower():
                continue
            body_entries.append({
                "ref": ref,
                "translation": "NIV",
                "cue": heading,
                "note": "",
                "text": "[VERIFY & PASTE VERBATIM NIV TEXT HERE]",
            })
    elif found:
        first_ref, first_heading, _ = found[0]
        meta["opening_ref"] = first_ref
        opening_entries.append({
            "ref": first_ref,
            "translation": "KJV",
            "cue": "Stand for the reading of the Word",
            "note": f"First reference found in: {first_heading}",
            "text": "[VERIFY & PASTE VERBATIM KJV TEXT HERE]",
        })
        for ref, heading, _ in found[1:]:
            body_entries.append({
                "ref": ref,
                "translation": "NIV",
                "cue": heading,
                "note": "",
                "text": "[VERIFY & PASTE VERBATIM NIV TEXT HERE]",
            })

    return meta, opening_entries, body_entries


def write_structured_markdown(meta: dict[str, str], opening: list[dict], body: list[dict], out_path: Path) -> None:
    lines = [
        "---",
        f'title: "{meta.get("title", "Sermon Title")}"',
        f'date: "{meta.get("date", "YYYY-MM-DD")}"',
        f'series: "{meta.get("series", "")}"',
        f'church: "{meta.get("church", "Straight Creek Church of God")}"',
        f'preacher: "{meta.get("preacher", "Kyle Morrow")}"',
        f'opening_ref: "{meta.get("opening_ref", "")}"',
        "---",
        "",
        "## Opening Reading [KJV]",
        "",
    ]

    for item in opening:
        lines.append(f"### {item['ref']} (KJV)")
        if item.get("cue"):
            lines.append(f"<!-- Cue: {item['cue']} -->")
        if item.get("note"):
            lines.append(f"<!-- Note: {item['note']} -->")
        lines.append(f"> {item['text']}")
        lines.append("")

    lines.extend(["---", "", "## Body References [NIV]", ""])

    for item in body:
        lines.append(f"### {item['ref']} (NIV)")
        if item.get("cue"):
            lines.append(f"<!-- Movement: {item['cue']} -->")
        if item.get("note"):
            lines.append(f"<!-- Note: {item['note']} -->")
        lines.append(f"> {item['text']}")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def parse_structured_sheet(path: Path) -> tuple[dict[str, str], list[dict], list[dict]]:
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    meta.setdefault("title", path.stem.replace("-", " ").title())
    meta.setdefault("church", "Straight Creek Church of God")
    meta.setdefault("preacher", "Kyle Morrow")

    mode = "opening"
    opening: list[dict] = []
    body_refs: list[dict] = []
    current: dict | None = None

    def flush() -> None:
        nonlocal current
        if current is not None:
            current["text"] = "\n".join(current["text_lines"]).strip()
            del current["text_lines"]
            if current["section"] == "opening":
                opening.append(current)
            else:
                body_refs.append(current)
            current = None

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            flush()
            lower = stripped.lower()
            mode = "opening" if "opening" in lower or "kjv" in lower else "body"
            continue

        if stripped.startswith("### "):
            flush()
            heading = stripped[4:].strip()
            trans_match = re.search(r"\((KJV|NIV|ESV|NLT|NKJV|CSB)\)\s*$", heading, re.IGNORECASE)
            if trans_match:
                translation = trans_match.group(1).upper()
                ref = heading[: trans_match.start()].strip()
            else:
                translation = "KJV" if mode == "opening" else "NIV"
                ref = heading
            current = {
                "ref": ref,
                "translation": translation,
                "cue": "",
                "note": "",
                "section": mode,
                "text_lines": [],
            }
            continue

        if current is None:
            continue

        cue_match = re.match(r"^<!--\s*(?:Cue|Movement)\s*:\s*(.*?)\s*-->$", stripped, re.IGNORECASE)
        if cue_match:
            current["cue"] = cue_match.group(1).strip()
            continue

        note_match = re.match(r"^<!--\s*Note\s*:\s*(.*?)\s*-->$", stripped, re.IGNORECASE)
        if note_match:
            current["note"] = note_match.group(1).strip()
            continue

        if stripped == "---":
            continue

        if stripped.startswith(">"):
            text_line = stripped[1:].lstrip()
            current["text_lines"].append(text_line)
        elif stripped:
            current["text_lines"].append(stripped)
        elif current["text_lines"]:
            current["text_lines"].append("")

    flush()
    return meta, opening, body_refs


def format_verse_html(text: str) -> str:
    """Format verified Scripture text cleanly, styling bold verse numbers like **1** or [1]."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    rendered: list[str] = []
    for para in paragraphs:
        esc = html.escape(para)
        # Convert **12** into superscript verse number badge
        esc = re.sub(r"\*\*(\d+)\*\*", r'<sup class="vnum">\1</sup>', esc)
        # Convert [12] into superscript verse number badge (unless it's a placeholder)
        if "VERIFY &amp; PASTE" not in esc:
            esc = re.sub(r"\[(\d+)\]", r'<sup class="vnum">\1</sup>', esc)
        # Convert *italic* to <em>
        esc = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", esc)
        # Highlight unverified placeholder loudly so it is never missed before printing
        if "VERIFY &amp; PASTE" in esc:
            rendered.append(f'<p class="placeholder">{esc}</p>')
        else:
            rendered.append(f"<p>{esc}</p>")
    return "\n".join(rendered)


def render_printable_html(meta: dict[str, str], opening: list[dict], body: list[dict]) -> str:
    title = html.escape(meta.get("title", "Sermon Scripture Sheet"))
    date = html.escape(meta.get("date", ""))
    series = html.escape(meta.get("series", ""))
    church = html.escape(meta.get("church", "Straight Creek Church of God"))
    preacher = html.escape(meta.get("preacher", "Kyle Morrow"))

    meta_bits = [b for b in [series, date, church] if b and b != "YYYY-MM-DD"]
    subtitle = " &middot; ".join(meta_bits)

    opening_summary = ", ".join(item["ref"] for item in opening) or meta.get("opening_ref", "")
    body_summary = " &bull; ".join(item["ref"] for item in body)

    opening_cards: list[str] = []
    for item in opening:
        cue_html = f'<div class="cue">{html.escape(item["cue"])}</div>' if item.get("cue") else ""
        note_html = f'<div class="note">{html.escape(item["note"])}</div>' if item.get("note") else ""
        opening_cards.append(
            f"""
            <section class="card opening-card">
              <div class="card-head">
                <div class="ref-group">
                  <span class="badge badge-kjv">{html.escape(item['translation'])} &mdash; OPENING READING</span>
                  <h2 class="ref-title">{html.escape(item['ref'])}</h2>
                </div>
                {cue_html}
              </div>
              {note_html}
              <div class="verse-body">
                {format_verse_html(item['text'])}
              </div>
              <div class="order-strip">
                Order: Stand &rarr; Read KJV &rarr; Title &amp; Prayer &rarr; &ldquo;You may be seated&rdquo; &rarr; Hook / Intro
              </div>
            </section>
            """
        )

    body_cards: list[str] = []
    for idx, item in enumerate(body, start=1):
        cue_html = f'<div class="cue">{html.escape(item["cue"])}</div>' if item.get("cue") else ""
        note_html = f'<div class="note">{html.escape(item["note"])}</div>' if item.get("note") else ""
        body_cards.append(
            f"""
            <article class="card body-card">
              <div class="card-head">
                <div class="ref-group">
                  <span class="seq-num">{idx}</span>
                  <h3 class="ref-title">{html.escape(item['ref'])}</h3>
                  <span class="badge badge-niv">{html.escape(item['translation'])}</span>
                </div>
                {cue_html}
              </div>
              {note_html}
              <div class="verse-body">
                {format_verse_html(item['text'])}
              </div>
            </article>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Pulpit Scripture Sheet: {title}</title>
  <style>
    @page {{
      size: letter;
      margin: 0.6in 0.65in;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      font-family: Georgia, "Times New Roman", serif;
      color: #111827;
      background: #f3f4f6;
      margin: 0;
      padding: 24px;
      line-height: 1.55;
    }}

    .sheet {{
      max-width: 8.2in;
      margin: 0 auto;
      background: #ffffff;
      padding: 0.45in 0.5in;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    }}

    .print-bar {{
      max-width: 8.2in;
      margin: 0 auto 14px auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 13px;
      color: #4b5563;
    }}

    .print-btn {{
      background: #111827;
      color: #ffffff;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
    }}

    .print-btn:hover {{
      background: #1f2937;
    }}

    .doc-header {{
      border-bottom: 2.5px solid #111827;
      padding-bottom: 12px;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      gap: 16px;
    }}

    .doc-header h1 {{
      margin: 0 0 4px 0;
      font-size: 22pt;
      line-height: 1.15;
      letter-spacing: -0.01em;
    }}

    .doc-meta {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 10pt;
      color: #4b5563;
    }}

    .doc-label {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 9pt;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #374151;
      text-align: right;
      white-space: nowrap;
    }}

    .glance-strip {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 9.5pt;
      background: #f9fafb;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      padding: 8px 12px;
      margin-bottom: 18px;
      color: #1f2937;
    }}

    .glance-strip strong {{
      color: #111827;
    }}

    .section-divider {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 10pt;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #374151;
      border-bottom: 1.5px solid #9ca3af;
      padding-bottom: 4px;
      margin: 22px 0 14px 0;
    }}

    .card {{
      break-inside: avoid;
      page-break-inside: avoid;
      margin-bottom: 16px;
      border-radius: 6px;
    }}

    .opening-card {{
      border: 2px solid #111827;
      padding: 16px 18px 12px 18px;
      background: #fcfcfd;
    }}

    .body-card {{
      border: 1px solid #d1d5db;
      border-left: 4px solid #374151;
      padding: 12px 16px;
    }}

    .card-head {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }}

    .ref-group {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .seq-num {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #111827;
      color: #ffffff;
      font-size: 10pt;
      font-weight: 700;
    }}

    .ref-title {{
      margin: 0;
      font-size: 15pt;
      font-weight: 700;
      color: #111827;
    }}

    .badge {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 8.5pt;
      font-weight: 700;
      letter-spacing: 0.06em;
      padding: 3px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }}

    .badge-kjv {{
      background: #111827;
      color: #ffffff;
    }}

    .badge-niv {{
      background: #e5e7eb;
      color: #111827;
      border: 1px solid #9ca3af;
    }}

    .cue {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 9.5pt;
      font-weight: 600;
      color: #374151;
    }}

    .note {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 9.5pt;
      font-style: italic;
      color: #4b5563;
      margin-bottom: 8px;
    }}

    .verse-body {{
      font-size: 14pt;
      line-height: 1.58;
      color: #111827;
    }}

    .opening-card .verse-body {{
      font-size: 14.5pt;
    }}

    .verse-body p {{
      margin: 0 0 8px 0;
    }}

    .verse-body p:last-child {{
      margin-bottom: 0;
    }}

    .vnum {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 9pt;
      font-weight: 700;
      color: #4b5563;
      margin-right: 3px;
    }}

    .placeholder {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 10.5pt;
      font-weight: 700;
      color: #991b1b;
      background: #fef2f2;
      border: 1px dashed #dc2626;
      padding: 8px 10px;
      border-radius: 4px;
    }}

    .order-strip {{
      margin-top: 12px;
      padding-top: 8px;
      border-top: 1px solid #e5e7eb;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 9pt;
      font-weight: 600;
      color: #374151;
    }}

    @media print {{
      body {{
        background: #ffffff;
        padding: 0;
      }}
      .print-bar {{
        display: none;
      }}
      .sheet {{
        max-width: none;
        padding: 0;
        box-shadow: none;
      }}
    }}
  </style>
</head>
<body>
  <div class="print-bar">
    <span>Pulpit Scripture Sheet &mdash; Large Print (14&ndash;14.5pt) &mdash; Ready for US Letter Print / PDF</span>
    <button class="print-btn" onclick="window.print()">Print / Save as PDF</button>
  </div>

  <main class="sheet">
    <header class="doc-header">
      <div>
        <h1>{title}</h1>
        <div class="doc-meta">{subtitle}</div>
      </div>
      <div class="doc-label">Pulpit Scripture Sheet<br />{preacher}</div>
    </header>

    <div class="glance-strip">
      <strong>Opening (KJV):</strong> {html.escape(opening_summary)}
      {f' &nbsp;|&nbsp; <strong>Body (NIV):</strong> {body_summary}' if body_summary else ''}
    </div>

    {''.join(opening_cards)}

    <div class="section-divider">Sermon Body References &mdash; NIV (In Preaching Order)</div>

    {''.join(body_cards) if body_cards else '<p class="doc-meta">No body references listed yet.</p>'}
  </main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a printable KJV/NIV Pulpit Scripture Reference Sheet.")
    parser.add_argument("input", nargs="?", type=Path, help="Structured scripture-refs.md file to render into printable HTML")
    parser.add_argument("--from-manuscript", type=Path, help="Extract references in order from a sermon manuscript (.md)")
    parser.add_argument("--out", type=Path, required=True, help="Output path (.md when extracting skeleton, .html when rendering printable sheet)")
    args = parser.parse_args()

    if args.from_manuscript:
        if not args.from_manuscript.exists():
            print(f"Error: manuscript not found: {args.from_manuscript}", file=sys.stderr)
            return 2
        meta, opening, body = extract_from_manuscript(args.from_manuscript)
        if args.out.suffix.lower() == ".html":
            rendered = render_printable_html(meta, opening, body)
            args.out.write_text(rendered, encoding="utf-8")
            print(f"Wrote printable HTML index sheet ({len(opening)} KJV opening, {len(body)} NIV body refs) -> {args.out}")
            print("NOTE: Paste verified verbatim KJV/NIV text into a scripture-refs.md sheet before Sunday printing.")
        else:
            write_structured_markdown(meta, opening, body, args.out)
            print(f"Extracted {len(opening)} KJV opening + {len(body)} NIV body refs -> {args.out}")
            print("Next: verify and paste verbatim KJV/NIV text, then render to printable HTML:")
            print(f"  python3 scripts/make_scripture_sheet.py {args.out} --out {args.out.with_suffix('.html')}")
        return 0

    if not args.input:
        parser.error("Provide a structured scripture-refs.md file OR use --from-manuscript <draft.md>")

    if not args.input.exists():
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        return 2

    meta, opening, body = parse_structured_sheet(args.input)
    rendered = render_printable_html(meta, opening, body)
    args.out.write_text(rendered, encoding="utf-8")

    unverified = sum(1 for item in opening + body if "VERIFY & PASTE" in item.get("text", ""))
    print(f"Wrote printable Pulpit Scripture Sheet ({len(opening)} KJV opening, {len(body)} NIV body refs) -> {args.out}")
    if unverified:
        print(f"[WARN] {unverified} passage(s) still have unverified placeholders. Paste verbatim text before printing!")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
