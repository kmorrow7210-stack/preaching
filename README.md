# preaching

Kyle Morrow's preaching workspace. It holds sermon research, manuscripts, homiletics study, voice analysis, printable pulpit tools, and long-form preaching projects.

## Repository map

- **[`AGENTS.md`](AGENTS.md)**: The single rules file for every AI tool working here (Hermes Agent, Muse Code, Grok Build, Codex, Antigravity, and chat assistants). Update it whenever a standing rule changes.
- **[`about-me.md`](about-me.md)**: Who Kyle is, how he works, his theological framework, and his voice rules.
- **`sermons/`**: Active sermon folders (`sermons/YYYY-MM-DD-short-title/`) and archived past sermons in Markdown (`sermons/archive/`, with original PDFs preserved in `sermons/archive/pdfs/`).
- **`voice/`**: Current preaching voice profile (`voice/Kyle-Preaching-Voice-Profile.md`), `voice/transcripts/current/` (active baseline for voice calibration), and `voice/transcripts/archive/` (older transcripts kept strictly for historical comparison, not as a style target).
- **`craft/`**: Homiletics study notes (`What-Does-The-Sermon-Do.md`), the 5-stage inductive template (`Inductive-Plot-Template.md`), and the Gritty Narrative feedback rubric (`Homiletic-Feedback-Toolkit.md`).
- **`templates/`**: Ready-to-copy templates for a new sermon (`PROJECT_BRIEF.md`, `SERMON_OUTLINE.md`, `SCRIPTURE_SHEET.md`, and `POST_SUNDAY_REVIEW.md`).
- **`library/`**: Cross-sermon memory (`SERMON_INDEX.md` and `ILLUSTRATIONS.md`) to track series callbacks and avoid repeating stories unintentionally.
- **`projects/`**: Long-form projects kept separate from weekly sermon prep, including the D.Min. dissertation rewrite and repurposing report in `projects/preaching-theologically/`.
- **`scripts/`**: Pre-pulpit utilities:
  - `scripts/check_draft.py`: Checks word count, estimated pulpit runtime at 110 manuscript words/minute, banned AI words, em dashes, backpedal phrasing, and Scripture citations.
  - `scripts/make_scripture_sheet.py`: Generates a clean, large-print printable pulpit Scripture sheet with the opening reading in **KJV** and body references in **NIV** in exact sermon order.
