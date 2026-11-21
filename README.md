# preaching

Kyle Morrow's preaching workspace. GitHub is the canonical source of truth; Google Drive (`preaching/`) is maintained as a readable 1:1 mirror refreshed from this repository.

## Repository map

- **[`AGENTS.md`](AGENTS.md)**: The single rules file for every AI tool working here (Hermes Agent, Muse Code, Grok Build, Codex, Antigravity, and chat assistants). Update it whenever a standing rule changes.
- **[`about-me.md`](about-me.md)**: Who Kyle is, how he works, his theological framework, and his voice rules.
- **`sermons/`**:
  - `sermons/YYYY-MM-DD-short-title/`: Active and recent sermon packets (`PROJECT_BRIEF.md`, outlines, manuscripts, Scripture sheets).
  - `sermons/archive/2026-straight-creek/`: Completed 2026 Straight Creek sermon manuscripts and drafts.
  - `sermons/archive/older-or-unclear/`: Older (2024–2025) and undated sermon manuscripts in Markdown (kept for historical comparison only; original PDFs preserved in `sermons/archive/pdfs/`).
- **`voice/`**:
  - `voice/Kyle-Preaching-Voice-Profile.md`: Current preaching voice profile, refreshed from Straight Creek transcripts and weighted toward recent Mark sermons.
  - `voice/Preaching-Diagnostic-Manuscript-vs-Transcript.md`: Side-by-side delivery geography study (pulpit vs. floor zones).
  - `voice/transcripts/current/`: Verified Straight Creek delivered transcripts (active voice baseline).
  - `voice/transcripts/archive/`: Older/unclear-era transcripts kept strictly for longitudinal comparison, never as a drafting target.
- **`craft/`**: Homiletics study notes (`What-Does-The-Sermon-Do.md`), the 5-stage inductive template (`Inductive-Plot-Template.md`), and the Gritty Narrative feedback rubric (`Homiletic-Feedback-Toolkit.md`).
- **`templates/`**: Ready-to-copy starters (`PROJECT_BRIEF.md`, `SERMON_OUTLINE.md`, `SCRIPTURE_SHEET.md`, and `POST_SUNDAY_REVIEW.md`).
- **`library/`**: Cross-sermon memory (`SERMON_INDEX.md` and `ILLUSTRATIONS.md`) to track series callbacks and avoid repeating stories unintentionally.
- **`projects/`**: Long-form projects separated from weekly prep, including `projects/preaching-theologically/`.
- **`scripts/`**: Pre-pulpit utilities:
  - `scripts/check_draft.py`: Checks word count, estimated pulpit runtime at 110 manuscript words/minute, banned AI words, em dashes, backpedal phrasing, and Scripture citations.
  - `scripts/make_scripture_sheet.py`: Generates a clean, large-print printable pulpit Scripture sheet with the opening reading in **KJV** and body references in **NIV** in exact sermon order.
