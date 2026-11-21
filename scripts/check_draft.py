#!/usr/bin/env python3
"""
Pre-pulpit draft checker for Kyle Morrow's preaching workspace.

Checks:
  - Spoken word count and estimated pulpit runtime (default 110 manuscript wpm)
  - Section-by-section pacing breakdown
  - Em dashes (banned by Fire & Footnotes voice rules)
  - Banned AI words (dwell, delve, tapestry, realm, robust, nuanced, utilize, leverage)
  - Backpedal / hedging phrases & defensive apologies (advisory)
  - Opening order & protected ending markers
  - Ordered list of Scripture references for KJV/NIV verification

Usage:
  python3 scripts/check_draft.py path/to/manuscript.md [--target-minutes 40] [--wpm 110]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BANNED_WORD_PATTERNS = [
    (r"\bdwell(?:s|ed|ing)?\b", "dwell"),
    (r"\bdelv(?:e|es|ed|ing)\b", "delve"),
    (r"\btapestr(?:y|ies)\b", "tapestry"),
    (r"\brealm(?:s)?\b", "realm"),
    (r"\brobust(?:ly|ness)?\b", "robust"),
    (r"\bnuanc(?:e|ed|es)\b", "nuanced"),
    (r"\butiliz(?:e|es|ed|ing|ation)\b", "utilize"),
    (r"\bleverag(?:e|es|ed|ing)\b", "leverage"),
]

BACKPEDAL_PATTERNS = [
    (r"\bmaybe\b", "maybe"),
    (r"\bperhaps\b", "perhaps"),
    (r"\bpossibly\b", "possibly"),
    (r"\bin a sense\b", "in a sense"),
    (r"\bI think\b", "I think"),
]

APOLOGY_PATTERNS = [
    r"\bI(?:'|’)?m sorry if\b",
    r"\bsorry if this is hard\b",
    r"\bI know this text is difficult\b",
    r"\bkeep you (?:here )?(?:all day|too long|long)\b",
]

# Full + common abbreviated Bible book names (ordered longest-first to avoid partial matches)
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


def strip_frontmatter(lines: list[str]) -> tuple[dict[str, str], list[tuple[int, str]]]:
    """Return (frontmatter_dict, list of (1-indexed line_no, text))."""
    meta: dict[str, str] = {}
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                for fm_line in lines[1:idx]:
                    if ":" in fm_line:
                        k, v = fm_line.split(":", 1)
                        meta[k.strip().lower()] = v.strip().strip('"').strip("'")
                return meta, [(i + 1, lines[i]) for i in range(idx + 1, len(lines))]
    return meta, [(i + 1, lines[i]) for i in range(len(lines))]


def clean_for_wordcount(text: str) -> str:
    """Remove Markdown syntax, HTML comments, and bracketed stage cues for spoken word count."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    # Remove bracketed cues like [Read Revelation 13:1-10] or [PROTECTED]
    text = re.sub(r"\\?\[[^\]]*\\?\]", " ", text)
    # Remove Markdown headings markers, emphasis, blockquote markers, horizontal rules
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-—*]{3,}\s*$", " ", text, flags=re.MULTILINE)
    text = re.sub(r"[*_`>#|]", " ", text)
    return text


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?", text))


def snippet(line: str, limit: int = 88) -> str:
    clean = " ".join(line.strip().split())
    return clean if len(clean) <= limit else clean[: limit - 3] + "..."


def detect_heading(stripped: str) -> str | None:
    if stripped.startswith("#"):
        return re.sub(r"^#+\s*", "", stripped).strip("*_ ")
    # Also recognize standalone bold Roman/section headers like **I. TWO PARADES**
    m = re.match(r"^\*\*([I|V|X]+\.\s+[^*]+|[A-Z0-9][A-Z0-9\s:.'’\-–—]+)\*\*$", stripped)
    if m and len(m.group(1)) <= 80:
        return m.group(1).strip()
    return None


def analyze(path: Path, target_minutes: int, wpm: int) -> int:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    meta, body_lines = strip_frontmatter(lines)

    # Track sections and word counts
    sections: list[dict] = []
    current_section = {"heading": "(Opening / Before First Heading)", "start_line": 1, "lines": []}

    em_dashes: list[tuple[int, str]] = []
    banned_hits: list[tuple[int, str, str]] = []
    backpedal_hits: list[tuple[int, str, str]] = []
    apology_hits: list[tuple[int, str]] = []
    scriptures: list[tuple[int, str, str]] = []
    protected_lines: list[int] = []

    cold_open_line: int | None = None
    first_scripture_cue_line: int | None = None
    altar_start_words: int | None = None
    running_words = 0

    for line_no, line in body_lines:
        stripped = line.strip()

        # Headings
        heading_text = detect_heading(stripped)
        if heading_text is not None:
            if current_section["lines"]:
                sections.append(current_section)
            current_section = {"heading": heading_text, "start_line": line_no, "lines": []}
            if re.search(r"\bcold open\b", heading_text, re.IGNORECASE) and cold_open_line is None:
                cold_open_line = line_no
            if re.search(r"\b(altar|closing|invitation)\b", heading_text, re.IGNORECASE) and altar_start_words is None:
                altar_start_words = running_words
            if re.search(r"\b(scripture reading|opening reading)\b", heading_text, re.IGNORECASE) and first_scripture_cue_line is None:
                first_scripture_cue_line = line_no
            continue

        current_section["lines"].append((line_no, line))
        running_words += count_words(clean_for_wordcount(line))

        if "[PROTECTED]" in line:
            protected_lines.append(line_no)

        if first_scripture_cue_line is None and re.search(r"\[(?:Read|Opening Reading|KJV)", line, re.IGNORECASE):
            first_scripture_cue_line = line_no

        # Skip pure Markdown rules when checking em dashes
        if not re.match(r"^\s*[-—*_ ]{3,}\s*$", stripped):
            if "—" in line or re.search(r"\S\s*--\s*\S", line):
                em_dashes.append((line_no, snippet(line)))

        # Banned words
        for pat, label in BANNED_WORD_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                banned_hits.append((line_no, label, snippet(line)))

        # Backpedal words (advisory)
        for pat, label in BACKPEDAL_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                backpedal_hits.append((line_no, label, snippet(line)))

        # Defensive apologies
        for pat in APOLOGY_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                apology_hits.append((line_no, snippet(line)))

        # Scripture references
        for m in SCRIPTURE_RE.finditer(line):
            ref = " ".join(m.group(0).split())
            # Ignore false positives like "John 1918" or "Acts 2026" (years)
            nums = re.findall(r"\d+", ref)
            if nums and int(nums[0]) > 150:
                continue
            scriptures.append((line_no, current_section["heading"], ref))

    if current_section["lines"]:
        sections.append(current_section)

    total_words = sum(
        count_words(clean_for_wordcount("\n".join(text for _, text in sec["lines"])))
        for sec in sections
    )
    est_minutes = total_words / wpm if wpm else 0.0
    target_words = target_minutes * wpm
    delta_words = total_words - target_words
    delta_min = est_minutes - target_minutes

    # Print Report
    print("=" * 72)
    print(f"PRE-PULPIT DRAFT CHECK: {path}")
    print("=" * 72)

    if meta:
        meta_summary = " | ".join(f"{k}: {v}" for k, v in meta.items() if k in {"title", "date", "series", "opening_ref"})
        if meta_summary:
            print(f"Metadata: {meta_summary}")

    print("\n1. PACING & LENGTH (Measured Pace: {} manuscript wpm)".format(wpm))
    print(f"   Spoken words:     {total_words:,}")
    print(f"   Estimated pulpit: {est_minutes:.1f} min  (Target: {target_minutes} min / ~{target_words:,} words)")
    if delta_min > 3.0:
        print(f"   [WARN] Over budget by ~{delta_min:.1f} min (~{delta_words:+,} words). Trim early sections to protect the altar.")
    elif delta_min < -5.0:
        print(f"   [INFO] Under budget by ~{abs(delta_min):.1f} min (~{abs(delta_words):,} words). Plenty of room for live expansion.")
    else:
        print("   [OK]   Right in the target window.")

    print("\n   Section breakdown:")
    for sec in sections:
        sec_words = count_words(clean_for_wordcount("\n".join(text for _, text in sec["lines"])))
        if sec_words == 0:
            continue
        sec_min = sec_words / wpm
        pct = (sec_words / total_words * 100) if total_words else 0
        print(f"   - L{sec['start_line']:<4} {sec['heading'][:42]:<42} {sec_words:>5} words  (~{sec_min:>4.1f} min | {pct:>4.1f}%)")

    print("\n2. STRUCTURE & OPENING ORDER")
    if cold_open_line is not None and (first_scripture_cue_line is None or cold_open_line < first_scripture_cue_line):
        print(f"   [WARN] 'Cold Open' heading on L{cold_open_line} appears before Scripture reading (L{first_scripture_cue_line or '?'}).")
        print("          Standing rule: Stand -> KJV Reading -> Prayer -> Sit -> Hook / Intro.")
    else:
        print("   [OK]   No hook/cold-open heading detected ahead of opening Scripture reading.")

    if protected_lines:
        print(f"   [OK]   Found {len(protected_lines)} [PROTECTED] ending marker(s) at line(s): {', '.join(f'L{n}' for n in protected_lines)}")
    else:
        print("   [INFO] No [PROTECTED] ending markers tagged yet. Consider tagging key closing/altar lines.")

    if altar_start_words is not None and total_words > 0:
        altar_pct = altar_start_words / total_words * 100
        if altar_pct > 92:
            print(f"   [WARN] Closing/Altar section starts at {altar_pct:.1f}% of manuscript; make sure it has breathing room.")
        else:
            print(f"   [OK]   Closing/Altar section starts at {altar_pct:.1f}% of manuscript.")

    print("\n3. FIRE & FOOTNOTES VOICE LINT")
    if em_dashes:
        print(f"   [WARN] Em dashes found: {len(em_dashes)} line(s) (rule: no em dashes)")
        for ln, sn in em_dashes[:12]:
            print(f"          L{ln}: {sn}")
        if len(em_dashes) > 12:
            print(f"          ... and {len(em_dashes) - 12} more line(s)")
    else:
        print("   [OK]   Zero em dashes.")

    if banned_hits:
        print(f"   [WARN] Banned words found: {len(banned_hits)}")
        for ln, word, sn in banned_hits:
            print(f"          L{ln} [{word}]: {sn}")
    else:
        print("   [OK]   Zero banned words.")

    print("\n4. GRITTY NARRATIVE ADVISORY (Review, don't auto-scrub pastoral warmth)")
    if apology_hits:
        print(f"   [WARN] Potential defensive apology / length apology: {len(apology_hits)}")
        for ln, sn in apology_hits:
            print(f"          L{ln}: {sn}")
    else:
        print("   [OK]   No defensive apology phrasing detected.")

    if backpedal_hits:
        print(f"   [INFO] Backpedal / hedging hits: {len(backpedal_hits)} (keep honest pastoral reflection; sharpen weak hedges)")
        for ln, word, sn in backpedal_hits[:10]:
            print(f"          L{ln} [{word}]: {sn}")
        if len(backpedal_hits) > 10:
            print(f"          ... and {len(backpedal_hits) - 10} more")
    else:
        print("   [OK]   Zero backpedal words detected.")

    print("\n5. SCRIPTURE REFERENCES IN ORDER (Verify Opening = KJV, Body = NIV)")
    if scriptures:
        seen_order: list[tuple[int, str, str]] = []
        seen_keys: set[str] = set()
        for ln, sec_name, ref in scriptures:
            key = ref.lower()
            if key not in seen_keys:
                seen_keys.add(key)
                seen_order.append((ln, sec_name, ref))
        for idx, (ln, sec_name, ref) in enumerate(seen_order, start=1):
            trans = "KJV (Opening?)" if idx == 1 else "NIV (Body)"
            print(f"   {idx:>2}. {ref:<24} [{trans:<14}]  L{ln:<4} ({sec_name})")
    else:
        print("   [INFO] No explicit chapter:verse references detected.")

    print("=" * 72)
    has_warnings = bool(em_dashes or banned_hits or delta_min > 3.0)
    return 1 if has_warnings else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-pulpit draft checker for Kyle Morrow's sermons.")
    parser.add_argument("draft", type=Path, help="Path to Markdown sermon draft or outline")
    parser.add_argument("--target-minutes", type=int, default=40, help="Target Sunday pulpit length in minutes (default: 40)")
    parser.add_argument("--wpm", type=int, default=110, help="Manuscript words per pulpit minute (default: 110)")
    args = parser.parse_args()

    if not args.draft.exists():
        print(f"Error: file not found: {args.draft}", file=sys.stderr)
        return 2

    return analyze(args.draft, args.target_minutes, args.wpm)


if __name__ == "__main__":
    raise SystemExit(main())
