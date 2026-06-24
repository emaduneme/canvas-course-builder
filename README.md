# canvas-course-builder

A Claude Code **plugin** that turns dropped course materials plus a short interview into
**verified, Canvas-importable artifacts** — quizzes and rubrics in v1 — governed by a single
`course-profile.yml`.

It grows the single-purpose `canvas-quiz-export` skill into a profile-driven, multi-subagent
pipeline: **intake → workers → verifier**. Every generated item must trace to a real source, and
nothing reaches the instructor until a verifier proves traceability and points integrity.

## What you get

| Artifact | Format |
|---|---|
| Quiz | IMS Common Cartridge 1.1.3 + QTI 1.2 package (zip → Canvas import) |
| Rubric | Canvas CC `rubrics.xml` (default) or paste-able CSV/markdown |
| Audit trail | `trace.json` beside each package (`item → {source_id, locator, points}` + checks) |

## Pipeline

```
/course-build  (or "build me a Canvas quiz")
   │
   ▼
intake ── interviews you, catalogs dropped files, runs research for
   │       type: research sources, writes course-profile.yml
   ▼
orchestrator (course-builder skill) ── loads + validates the profile, then dispatches:
   ├─► question-worker   (quiz_defaults + course + sources)  → tagged source.md → QTI package
   └─► rubric-worker     (rubric_defaults + course + sources) → rubric (criteria sum to total)
   ▼
verifier ── traceability + points + QTI structure → trace.json; honors on_verify_fail
   ▼
output.dir/  ← verified packages
```

Each worker reads **only its own section + `course` + `sources`** — context isolation enforced
by dispatching subagents with just their slice of the profile.

## Quick start

1. Drop your course files (syllabus, workbook, slides…) into a working directory.
2. Run `/course-build` (or just ask Claude to "build me a Canvas quiz").
3. Intake writes `course-profile.yml` — copied from
   [`templates/course-profile.template.yml`](templates/course-profile.template.yml). Review it.
4. Workers build; the verifier gates; verified packages land in `output.dir`.
5. Zip a quiz package and import via **Canvas → Course → Settings → Import Course Content →
   Common Cartridge 1.x Package**.

## Source traceability

Author inline tags on every question in `source.md`:

```
### Q3 (Multiple Choice) [src: workbook-ch3 §p.42] [points: 2]
```

The verifier enforces (when `quiz_defaults.source_tagging: required`): every item is tagged,
every tag's `source_id` exists in `sources:`, and item points sum to `points_possible`. For
rubrics, criteria points must sum to `total_points`.

## External research (optional)

A `sources` entry with `type: research` is gathered and cached to `sources/<id>.md` **before**
any question is written, so traceability holds. Provider resolution degrades gracefully:
**Perplexity → Apify → WebSearch**. Works out of the box with no keys (WebSearch). See
[`references/research-integration.md`](references/research-integration.md).

## Layout

```
.claude-plugin/plugin.json     plugin manifest
commands/course-build.md       /course-build entrypoint
agents/                        intake · question-worker · rubric-worker · verifier · module-worker (stub)
skills/
  course-builder/SKILL.md      orchestrator
  course-builder/scripts/      verify.py (checks + trace.json) · research_provider.py
  canvas-export/               QTI engine (copied from the canvas-quiz-export skill)
templates/course-profile.template.yml
references/                    profile-schema.md · research-integration.md
evals/                         run_evals.py (executable §8 evals) · fixtures/ · evals.json
```

## Verifying the plugin

```bash
python3 evals/run_evals.py        # §8 pipeline evals — exit 0 = all pass
```

The reference verifier (`skills/course-builder/scripts/verify.py`) is pure stdlib — it bundles a
small YAML-subset parser so it runs anywhere `python3` does, no `pip install` required.

## Scope (v1)

- **In:** intake, question-worker, rubric-worker, verifier; QTI quiz export; CC/CSV rubric export.
- **Deferred:** module building (`module-worker` ships as a documented stub); New Quizzes JSON
  export (`export_format` reserved).
- The global `~/.claude/skills/canvas-quiz-export/` skill is **not modified** — its engine is
  copied into `skills/canvas-export/`.

## License

MIT.
