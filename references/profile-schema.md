# course-profile.yml — field reference

`course-profile.yml` is the **single source of truth**. Indent with 2 spaces (no tabs). Unknown
fields are left `null` — workers must handle `null`, never guess.

## Ownership

Each worker is dispatched with **only its own section + `course` + `sources`** (context
isolation). This is the contract that maps the profile onto subagents.

| Section | Owner |
|---|---|
| `course` | everyone (shared) |
| `sources` | everyone (the verifier's anchor) |
| `quiz_defaults` | question-worker |
| `rubric_defaults` | rubric-worker |
| `module_defaults` | module-worker (deferred, `null` in v1) |
| `output` | every writer + verifier |

## `course`

| Field | Type | Notes |
|---|---|---|
| `code` | string\|null | e.g. `MC320-01` |
| `title` | string\|null | e.g. `Media News` |
| `term` | string\|null | e.g. `Spring 2026` |
| `institution` | string\|null | |
| `instructor` | string\|null | |

## `sources` (list)

Every artifact item must trace to one of these ids.

| Field | Type | Notes |
|---|---|---|
| `id` | string | short, kebab-case, **unique** — referenced by `[src: id …]` tags |
| `type` | enum | `workbook` \| `textbook` \| `syllabus` \| `slides` \| `notes` \| `research` \| `other` |
| `path` | string\|null | absolute path to a dropped file (file-backed types) |
| `query` | string\|null | search query (**`type: research` only**) |
| `cached_to` | string\|null | `sources/<id>.md` — intake writes the gathered, citeable result here (research) |
| `label` | string\|null | human label shown in `trace.json` |
| `covers` | string\|null | e.g. `"weeks 1-2"` |

## `quiz_defaults` (question-worker)

| Field | Type | Notes |
|---|---|---|
| `items_per_quiz` | int | number of questions |
| `question_types` | list | subset of `multiple_choice`, `true_false` |
| `points_per_item` | number | default per-item points when `[points: N]` is omitted in a tag |
| `difficulty_mix` | string\|null | e.g. `"easy:3, medium:5, hard:2"` |
| `blooms_target` | string\|null | e.g. `"remember, understand, apply"` |
| `time_limit` | int\|null | minutes, or `null` for none |
| `shuffle_answers` | bool | |
| `show_correct_answers` | bool | |
| `allowed_attempts` | int | `1`, or `-1` for unlimited |
| `workflow_state` | enum | `published` \| `unpublished` |
| `source_tagging` | enum | `required` (verifier enforces tags) \| `optional` |

## `rubric_defaults` (rubric-worker)

| Field | Type | Notes |
|---|---|---|
| `scale_type` | enum | `points` \| `ranges` |
| `total_points` | number | criteria points must sum to this |
| `criteria_count` | int | exact number of criteria to produce |
| `criteria_style` | string\|null | `analytic` \| `holistic` |
| `rating_levels` | int | performance levels per criterion |

## `module_defaults`

`null` in v1 (deferred). See `agents/module-worker.md`.

## `output`

| Field | Type | Notes |
|---|---|---|
| `dir` | string | where verified packages are written |
| `package_naming` | string | template, e.g. `"{slug}.zip"` |
| `on_verify_fail` | enum | `halt` (default — nothing ships until clean) \| `flag_and_continue` |
| `export_format` | enum | `qti` (only format wired in v1) |
| `rubric_export` | enum | `cc_rubrics` (default) \| `csv_markdown` (fallback) |

## `generated_at`

ISO 8601 timestamp stamped by intake.
