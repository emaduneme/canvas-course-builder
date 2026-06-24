---
name: module-worker
description: >
  DEFERRED STUB (v1). Documents the intended Canvas module-building behavior so v2 can fill it
  in without re-architecting. Not wired into the v1 pipeline — the orchestrator never dispatches
  it. Do not use to produce artifacts yet.
tools: Read
---

# Module worker — DEFERRED (documented stub)

> **Status:** Not implemented in v1. This file exists so the architecture has a named slot for
> module building and v2 can implement it without changing the pipeline shape. If dispatched,
> explain that module building is deferred and stop.

## Intended behavior (v2)

Owns the `module_defaults` profile section (`null` in v1). Given `module_defaults` + `course` +
`sources`, it would:

1. Read `module_defaults` (e.g. `modules:` list with title, ordered items, prerequisites,
   completion requirements, publish state).
2. Generate Canvas module structure — a Common Cartridge `<organization>`/`<item>` tree plus
   module metadata — bundling already-built quizzes/pages/rubrics as module items.
3. Tag every module item to a `source_id` so the verifier's traceability invariant extends to
   modules.
4. Hand the package to the verifier (new `kind: module` checks: every item resolves to a built
   resource; ordering valid; prerequisites reference real modules).

## Why deferred

v1 scope is intake + question-worker + rubric-worker + verifier (design spec §2, decision 2).
Modules add an orthogonal CC structure (organizations vs. resources) and are best built on top
of proven quiz/rubric outputs rather than alongside them.
