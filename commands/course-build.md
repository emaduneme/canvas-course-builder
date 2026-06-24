---
description: Build verified, Canvas-importable artifacts (quizzes + rubrics) from a course profile
---

# /course-build

Kick off the `canvas-course-builder` pipeline for the current working directory.

Invoke the **course-builder** orchestrator skill and run the full pipeline:

1. Dispatch the **intake** agent to interview me, catalog any files I've dropped here, run
   research for any `type: research` sources, and write/update `course-profile.yml`.
2. Load and validate the profile (halt if it does not parse).
3. Dispatch **question-worker** and **rubric-worker** in parallel, each with only its own
   profile section + `course` + `sources`. Skip any section that is `null` or not requested.
   Never dispatch the deferred module-worker.
4. Dispatch the **verifier** on every artifact; emit `trace.json`; honor
   `output.on_verify_fail` (`halt` by default — nothing ships until every check is green).
5. Write verified packages into `output.dir` and report what was built, where, and the
   `trace.json` audit paths.

Arguments (optional): `$ARGUMENTS` may name which artifacts to build (e.g. `quiz`, `rubric`,
`both`) or point at an existing `course-profile.yml`. If absent, ask during intake.

If there is no `course-profile.yml` yet, copy
`${CLAUDE_PLUGIN_ROOT}/templates/course-profile.template.yml` and fill it in during intake.
