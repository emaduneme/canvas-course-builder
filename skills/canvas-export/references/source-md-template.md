# source.md Template

Drop this template into `quizzes/[slug]/source.md` for any new quiz. It is the editable
source-of-truth from which the Canvas QTI/meta XML is generated. Keep it human-readable —
future-you (or a colleague) should be able to skim it and know exactly what's in the quiz.

```markdown
# [Quiz Title]

- **Quiz GUID:** `g[32-hex-chars]`
- **Course:** [Course code and section]
- **Authored:** [YYYY-MM-DD]
- **Sources:** [textbook chapters, lecture material, etc. — what the questions are drawn from]

## Settings

| Field | Value |
|---|---|
| Title | [Display name in Canvas] |
| Questions | [count] ([breakdown e.g. 8 MC + 6 T/F]) |
| Points | [total] ([points per question]) |
| Time limit | [N minutes or "none"] |
| Attempts | [1 or -1 for unlimited] |
| Shuffle answers | [true / false] |
| Show correct answers | [true / false] |
| Workflow | [published / unpublished] |
| Due | [ISO 8601 datetime or "none"] |

## Questions

### Q1 (Multiple Choice)
[Question text]
- A. [option A]
- **B. [option B]** ✓
- C. [option C]
- D. [option D]

**Rationale:** [optional — why this is correct]

### Q2 (True/False)
[Statement]

**Answer: True** ✓

**Rationale:** [optional]

[...repeat for each question...]

## Answer Key (quick reference)

| Q | Type | Answer |
|---|---|---|
| 1 | MC | B |
| 2 | T/F | True |
| ... | | |
```

## Conventions

- **Mark the correct answer** by bolding it and appending `✓` — both in the option list and in the rationale block for T/F.
- **Group questions by chapter or topic** with `###`-level headers if the quiz spans multiple units. Helps future revisions stay organized.
- **Include rationales** when authoring from textbook material — they're invaluable for grading appeals and for revising the question later.
- **Quote the GUID at the top** so the slug folder, package folder, and source.md are unambiguously linked.
- **Mark blank options as `(blank)`** — Canvas exports sometimes have placeholder empty answer slots; preserve them faithfully so re-imports match.
- **For reverse-extracted quizzes** (no original source preserved, generated from QTI XML), add a one-line note at the top: `> Source reverse-extracted from QTI XML. Edit this file to be the source-of-truth going forward; rebuild the package from here when revising.`
