# Canvas Course Builder — Design Spec

**Date:** 2026-06-24
**Status:** Approved (design); pending spec review → implementation plan
**Author:** intake/brainstorming session with Emmanuel Maduneme

---

## 1. Purpose

Grow the existing single-purpose global skill `canvas-quiz-export` into a self-contained,
shareable Claude Code **plugin** — `canvas-course-builder` — that turns dropped course
materials plus a short interview into **verified, Canvas-importable artifacts** (quizzes and
rubrics in v1), governed by `course-profile.yml` as the single source of truth.

The plugin is built as its own git repository so it can be published to GitHub independently
of any one course's content.

### Non-goals (v1)
- Module building (`module-worker`) — deferred; shipped as a documented stub only.
- New Quizzes JSON export — `qti` is the only export format wired in v1 (profile field
  reserved for later).
- Editing the user's existing global `canvas-quiz-export` skill. Its QTI engine is **copied**
  into the plugin so the current setup keeps working untouched.

---

## 2. Decisions (locked during brainstorming)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Packaging | Real Claude Code plugin with subagents (intake, workers, verifier) |
| 2 | v1 scope | intake + question-worker + rubric-worker + verifier; module-worker deferred |
| 3 | Traceability | Tags authored inline in `source.md`; verifier validates and emits `trace.json` audit artifact |
| 4 | External research | Optional Perplexity skill + Apify MCP, fallback to WebSearch; exposed as a `research` source type in intake |
| 5 | Location | `~/Desktop/SEMO/canvas-course-builder/` — standalone git repo for GitHub |

---

## 3. Repository structure

```
canvas-course-builder/                  ← git repo, shareable
├── .claude-plugin/plugin.json          ← plugin manifest
├── commands/
│   └── course-build.md                 ← /course-build entrypoint
├── agents/                             ← the subagents
│   ├── intake.md                       ← interview → writes course-profile.yml
│   ├── question-worker.md              ← profile.quiz + sources → tagged source.md → QTI
│   ├── rubric-worker.md                ← profile.rubric + sources → rubric
│   ├── verifier.md                     ← validates traceability/points → trace.json
│   └── module-worker.md                ← DEFERRED: documented stub only
├── skills/
│   ├── course-builder/SKILL.md         ← orchestrator (auto-triggers + runs pipeline)
│   └── canvas-export/                  ← QTI engine (copied from canvas-quiz-export)
│       ├── SKILL.md
│       └── references/{templates.md, source-md-template.md}
├── templates/
│   └── course-profile.template.yml     ← blank profile to drop into a course
├── references/
│   ├── profile-schema.md               ← field-by-field docs of course-profile.yml
│   └── research-integration.md         ← Apify/Perplexity/WebSearch fallback contract
├── evals/                              ← migrated quiz evals + new pipeline evals
└── README.md
```

---

## 4. The profile contract

`course-profile.yml` is the single source of truth. Its convention (carried from the
authored template):

> Workers read **ONLY their own section + `course` + `sources`**. If a field is unknown,
> leave it `null`. Workers must handle `null`, not guess.

This convention maps directly onto context-isolated subagents: each subagent is dispatched
with only the profile sections it owns.

Section ownership:

| Section | Owner |
|---------|-------|
| `course` | everyone (shared context) |
| `sources` | everyone (the verifier's anchor) |
| `quiz_defaults` | question-worker |
| `rubric_defaults` | rubric-worker |
| `module_defaults` | module-worker (deferred) |
| `output` | every writer + verifier |

A new source type is added to the `sources` schema:

```yaml
sources:
  - id: pr-ethics
    type: research          # NEW: workbook | textbook | syllabus | slides | notes | research | other
    query: "PR ethics codes 2024"   # used when type: research
    cached_to: sources/pr-ethics.md  # intake writes the gathered, citeable result here
    label: "PR ethics codes (researched)"
    covers: "week 6"
```

---

## 5. Pipeline / data flow

```
/course-build  (or casual "build me a Canvas quiz")
   │
   ▼
[intake subagent] ── interviews user, catalogs dropped files,
   │                  runs research for `type: research` sources (§7),
   │                  writes/updates course-profile.yml (stamps generated_at)
   ▼
[orchestrator skill] ── reads profile, dispatches workers in parallel:
   ├──► [question-worker]  reads quiz_defaults + course + sources only
   │        → tagged source.md → builds QTI package via canvas-export engine
   └──► [rubric-worker]    reads rubric_defaults + course + sources only
            → rubric artifact
   ▼
[verifier subagent] ── traceability + points checks → emits trace.json;
   │                    honors output.on_verify_fail (halt | flag_and_continue)
   ▼
output.dir/  ← verified packages, named per output.package_naming
```

### Component responsibilities

- **`/course-build` command** — thin entrypoint that kicks off intake explicitly. The
  orchestrator skill also auto-triggers on casual mentions ("make me a Canvas quiz").
- **intake** — conducts the interview, fills/updates `course-profile.yml`, catalogs dropped
  source files (absolute paths), runs research for `research`-type sources and caches them,
  stamps `generated_at`. Leaves unknown fields `null`.
- **orchestrator skill (`course-builder`)** — the brain. Loads the profile, validates it
  parses, dispatches the workers (parallel where independent), then the verifier, then writes
  to `output.dir`.
- **question-worker** — generates a tagged `source.md` per quiz (questions + inline source
  tags), then builds the QTI package using the copied `canvas-export` engine/templates.
  Honors `quiz_defaults` (items_per_quiz, question_types, difficulty_mix, blooms_target).
- **rubric-worker** — generates a rubric honoring `rubric_defaults` (scale_type,
  total_points, criteria_count, criteria_style, rating_levels). Criteria points must sum to
  `total_points`.
- **verifier** — see §6.
- **module-worker** — deferred. `agents/module-worker.md` exists as a documented stub
  describing intended behavior so v2 can fill it in without re-architecting.

---

## 6. Source traceability (verifier)

- Author tags **inline in `source.md`**, e.g. `Q3 [src: workbook-ch3 §p.42]`.
- Verifier validates, per the profile's `source_tagging: required`:
  1. every item carries a source tag;
  2. every tag's `source_id` exists in the profile's `sources:`;
  3. item points sum to the artifact's `points_possible` (quiz) / `total_points` (rubric);
  4. (existing QTI checks retained: unique GUIDs, correct-answer ident maps, manifest paths,
     HTML encoding).
- Verifier emits **`trace.json`** beside each package — a machine-readable map of
  `item → {source_id, locator}` — as a shareable audit trail.
- `output.on_verify_fail`:
  - `halt` (default) → nothing reaches the teacher until clean;
  - `flag_and_continue` → artifact passed through with an annotated warning.

---

## 7. Optional external research

When a source has `type: research`, intake gathers grounding material and **caches it to a
local citeable file** (`sources/<id>.md`) before any question is written — so the verifier
invariant (every item traces to a real source) never breaks.

Resolution order, each step gated on availability, degrading gracefully:

1. **Perplexity skill** — if the user has the key configured (existing `perplexity-search`
   skill). Preferred for grounded, cited answers.
2. **Apify MCP** — if available. For scraped/structured web sources.
3. **WebSearch** — always-available fallback, no key required.

`references/research-integration.md` documents how a cloner plugs in their own keys or just
uses WebSearch, so the plugin works out of the box for anyone.

---

## 8. Testing

- **Migrate** existing `canvas-quiz-export/evals/evals.json` cases into `evals/`.
- **Add** pipeline evals:
  - profile parsing (valid / null-handling / malformed);
  - traceability enforcement — an untagged item must trigger `halt`;
  - tag referencing a nonexistent `source_id` must fail;
  - points-sum mismatch (quiz and rubric) must fail;
  - research fallback selects WebSearch when no Perplexity/Apify key is present;
  - rubric criteria sum to `total_points`.
- **Dogfood end-to-end** on this course: the real `course-profile.yml` in
  `spring-2026-mc320-01-media-news-20878-quiz-export/` is test case #1.

---

## 9. Open question (to resolve in the implementation plan)

**Rubric export format.** Canvas has no clean Common Cartridge rubric import analogous to
QTI. Candidate formats:
- (a) Canvas course-settings `rubrics.xml` bundled into a CC package — consistent with the
  QTI flow; **recommended**, with (b) as fallback if CC rubric import proves flaky;
- (b) CSV/markdown rubric pasted into Canvas's rubric UI;
- (c) Canvas API JSON.

Resolution deferred to the implementation plan / a quick spike unless the user states a
preference first.

---

## 10. Migration & compatibility notes

- The global `~/.claude/skills/canvas-quiz-export/` skill is **not modified**. Its QTI
  engine and templates are **copied** into `skills/canvas-export/`. Once the plugin is
  proven, the user may optionally retire the standalone skill in favor of the plugin.
- The existing course repo's authoring conventions (`source.md` source-of-truth, GUID
  generation, answer-ID scheme, HTML encoding) are preserved verbatim in the copied engine.
```
