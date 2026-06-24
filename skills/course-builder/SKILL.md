---
name: course-builder
description: >
  Orchestrates building verified, Canvas-importable course artifacts (quizzes and rubrics in v1)
  from dropped materials plus a short interview, governed by course-profile.yml. Use whenever the
  user wants to build a Canvas quiz or rubric, mentions course-profile.yml, "build my course",
  "make me a Canvas quiz/rubric", or runs /course-build. Auto-triggers on casual mentions too.
---

# Course Builder — orchestrator

You are the brain of the `canvas-course-builder` plugin. You coordinate context-isolated
subagents around one source of truth: `course-profile.yml`. You do not author content yourself —
you dispatch the right agent with the right slice of the profile and gate everything on the
verifier.

## The pipeline

```
intake → (question-worker ∥ rubric-worker) → verifier → output.dir/
```

1. **Intake.** Dispatch the `intake` agent. It interviews the user, catalogs dropped files, runs
   research for `type: research` sources (caching to `sources/<id>.md`), and writes/updates
   `course-profile.yml`. Wait for it to report the profile path, source ids, and which artifacts
   were requested.

2. **Load + validate the profile.** Read `course-profile.yml`. Confirm it parses (the verifier's
   parser is authoritative — a malformed profile must halt the run, see §8 evals). Note
   `output.on_verify_fail`, `output.dir`, and which sections are non-null.

3. **Dispatch workers in parallel** (they share no state):
   - `question-worker` — pass **only** `quiz_defaults` + `course` + `sources`. It writes a tagged
     `source.md` and builds the QTI package via the copied `canvas-export` engine.
   - `rubric-worker` — pass **only** `rubric_defaults` + `course` + `sources`. It builds a rubric
     whose criteria sum to `total_points`.

   Skip a worker whose section is `null`/not requested. `module-worker` is **deferred** — never
   dispatch it in v1.

4. **Verify.** Dispatch the `verifier` agent on every built artifact. It runs
   `scripts/verify.py` (quiz traceability + points; qti structure; rubric sums), emits
   `trace.json` beside each package, and honors `output.on_verify_fail`:
   - `halt` → if any check fails, STOP; send the failed checks back to the relevant worker to
     fix and rebuild; re-verify. Nothing reaches the user until clean.
   - `flag_and_continue` → deliver with a prominent warning.

5. **Deliver.** Once verified, write/zip packages into `output.dir` per `output.package_naming`
   and report: artifacts built, where they are, and the `trace.json` paths.

## Section ownership (enforce this)

Workers read **only their own section + `course` + `sources`**. Do not hand the rubric-worker
`quiz_defaults`, etc. If a field is `null`, the worker handles it — you do not pre-fill guesses.

## Reference material

- Profile fields: `${CLAUDE_PLUGIN_ROOT}/references/profile-schema.md`
- Research fallback: `${CLAUDE_PLUGIN_ROOT}/references/research-integration.md`
- QTI engine: `${CLAUDE_PLUGIN_ROOT}/skills/canvas-export/` (SKILL.md + references/)
- Verifier + research resolver scripts: `${CLAUDE_PLUGIN_ROOT}/skills/course-builder/scripts/`
- Blank profile to copy: `${CLAUDE_PLUGIN_ROOT}/templates/course-profile.template.yml`

## Verifying the plugin itself

`python3 ${CLAUDE_PLUGIN_ROOT}/evals/run_evals.py` runs the §8 pipeline evals (exit 0 = all
pass). Run it after changing the verifier, the parser, or the research resolver.
