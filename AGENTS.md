# AGENTS.md

Workspace rules for every AI tool working in this repository (Hermes Agent, Meta Muse Code, xAI Grok Build, OpenAI Codex, Antigravity, or any chat assistant). Read this file before doing anything here.

## What this repo is for

This is Kyle Morrow's preaching workspace. Kyle is the pastor of Straight Creek Church of God (Fort Payne, AL), a Pentecostal congregation. The repo has four jobs:

1. **Prepare sermons:** study the text, build the brief, outline, draft, verify Scripture, and generate printable pulpit reference sheets.
2. **Study preaching:** homiletics, Pentecostal theology of preaching, and Th.M. / D.Min. work.
3. **Grow as a preacher:** compare delivered transcripts against manuscripts, track voice evolution over time, and give honest feedback.
4. **Repurpose preaching and dissertation work:** turn completed research into books, ministerial training, workshops, or Torn Veil essays and videos.

## Read first

1. `about-me.md`: who Kyle is, how he works, his theological lens, and his voice rules. These apply to everything in this repo.
2. `voice/Kyle-Preaching-Voice-Profile.md`: how Kyle actually preaches, built from current delivered sermon transcripts. Read it before drafting any manuscript, outline, illustration, or altar call in his voice. Run its closing checklist before calling a draft done.
3. The sermon's own `PROJECT_BRIEF.md` inside its folder (when one exists).

## Standing rules for sermon work

- **The project brief is the source of truth.** Each sermon has a brief (`PROJECT_BRIEF.md` in its folder, or a Notion prep page). Kyle edits it himself. Follow it over anything else, and do not overwrite it.
- **Text first:** the passage sets the agenda. Do the exegesis and study before writing. If the text has not been studied yet, start there.
- **Titles and illustrations are options until Kyle confirms them.** Present them as choices, never as settled.
- **Translations:** the opening public Scripture reading is **KJV**. Every later Scripture reference in the sermon body is **NIV**, unless Kyle says otherwise.
- **Verify every Scripture quotation against the actual text**, never from memory, and include exact book, chapter, and verse references.
- **Opening order is fixed:**
  1. Brief series placement and call to stand for the reading of the Word.
  2. Opening Scripture reading (**KJV**), with the congregation standing.
  3. Title announced (optional/customary right before prayer) and pulpit prayer.
  4. Congregation sits ("You may be seated...").
  5. Hook / intro story (never place a "cold open" or hook before the Scripture reading and prayer).
  6. Sermon body, closing bookend, open altar shaped by the sermon's image, and closing prayer.
- **Length and pacing math:** a Sunday sermon runs about 40 minutes. Kyle adds roughly half again live, so pace manuscripts at **about 110 manuscript words per minute** (~4,400 words for 40 minutes, ~3,500 words for 32 minutes). Keep early movements lean and mark protected ending lines with `[PROTECTED]` so the closing and altar call never pay for an overrun.
- **Sources:** never put words in a scholar's mouth. Flag any claim or connection that is not solidly sourced.
- **Voice:** plain, spoken pulpit language in Kyle's own theological framework (Divine Council, Second Temple Judaism, Pentecostal pneumatology), not generic evangelical phrasing. Follow `about-me.md` Fire and Footnotes rules: no em dashes, no banned words (`dwell`, `delve`, `tapestry`, `realm`, `robust`, `nuanced`, `utilize`, `leverage`), no fragment-stacking. Run the pulpit test before calling any draft done.
- **Transcripts rule:** only transcripts in `voice/transcripts/current/` define Kyle's current preaching voice. Files in `voice/transcripts/archive/` and `voice/archive/` exist strictly for longitudinal comparison and growth tracking, never as style references for new drafts.

## Pre-pulpit scripts

Run these from the repository root before finalizing a sermon:

- **Draft check (pacing, voice lint, references):**
  ```bash
  python3 scripts/check_draft.py sermons/YYYY-MM-DD-short-title/manuscript.md --target-minutes 40
  ```
- **Printable Pulpit Scripture Reference Sheet (KJV opening + NIV body references):**
  ```bash
  # Generate a structured Scripture sheet skeleton from a manuscript
  python3 scripts/make_scripture_sheet.py --from-manuscript sermons/YYYY-MM-DD-short-title/manuscript.md --out sermons/YYYY-MM-DD-short-title/scripture-refs.md

  # Render a large-print printable HTML sheet (print to paper or PDF from any browser)
  python3 scripts/make_scripture_sheet.py sermons/YYYY-MM-DD-short-title/scripture-refs.md --out sermons/YYYY-MM-DD-short-title/pulpit-scriptures.html
  ```

## Repository layout

| Path | What goes in it |
|---|---|
| `sermons/YYYY-MM-DD-short-title/` | Active and recent sermons: `PROJECT_BRIEF.md`, study notes, outline, manuscript, `scripture-refs.md`, printable HTML sheet, delivered transcript, and post-Sunday review |
| `sermons/archive/` | Past sermon manuscripts in Markdown (original PDFs preserved in `sermons/archive/pdfs/`) |
| `voice/` | Current voice profile (`Kyle-Preaching-Voice-Profile.md`), `transcripts/current/`, `transcripts/archive/` (comparison only), and `archive/` |
| `craft/` | Homiletics notes, `Inductive-Plot-Template.md`, and `Homiletic-Feedback-Toolkit.md` |
| `templates/` | Copy-ready starters (`PROJECT_BRIEF.md`, `SERMON_OUTLINE.md`, `SCRIPTURE_SHEET.md`, `POST_SUNDAY_REVIEW.md`) |
| `library/` | Cross-sermon memory: `SERMON_INDEX.md` and `ILLUSTRATIONS.md` |
| `projects/` | Long-form projects separated from weekly prep (such as `projects/preaching-theologically/`) |
| `scripts/` | Pre-pulpit draft checker and printable Scripture sheet generator |

## Boundaries and git workflow

- Do not move, rename, or delete Kyle's files without his approval. Add new files instead.
- Do not publish, send, or upload anything outside this repo without his approval.
- Do work on a branch and open a pull request for Kyle to review. Do not push straight to `main` unless he asks.
- At the end of a productive sermon session, leave a brief status note in that sermon's folder so the next tool or session can pick up cleanly.
- Kyle uses multiple AI tools (Hermes, Muse Code, Grok Build, Codex, Antigravity, and web chat tools). Never assume one tool owns the whole pipeline; ask if it is unclear which tool should handle a step.
