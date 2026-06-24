---
name: canvas-export
description: >
  Build Canvas LMS quiz packages in IMS Common Cartridge 1.1.3 + QTI 1.2 format that can be
  zipped and imported via Canvas Course > Settings > Import Course Content > Common Cartridge 1.x Package.
  Use this skill whenever the user mentions Canvas quizzes, quiz exports, QTI files, imsmanifest, 
  Common Cartridge, wants to create or add a quiz to a Canvas course, asks about quiz XML, 
  assessment_meta.xml, or wants to convert a question list into importable quiz files.
  Even if they say something casual like "make me a quiz for Canvas" — use this skill.
---

# Canvas Quiz Export Skill

You are generating files for Canvas LMS import. The output is always a directory that gets zipped 
and uploaded to Canvas. Every quiz needs exactly three things: a manifest, a QTI XML file, and a 
Canvas metadata file.

## Repository Layout (recommended for course repos)

When a project will hold multiple quizzes for a course, organize them like this:

```
[course-repo-root]/
├── README.md                                    ← human-readable index + how-to-add-a-quiz
├── CLAUDE.md                                    ← AI guide
├── imsmanifest.xml                              ← root multi-quiz manifest (paths into quizzes/)
├── quizzes/
│   └── [slug]/                                  ← kebab-case slug per quiz
│       ├── source.md                            ← question source-of-truth (edit this)
│       ├── [quiz-guid]/                         ← Canvas-importable package (per Package Structure)
│       │   ├── [quiz-guid].xml                  ← QTI 1.2 question data
│       │   ├── assessment_meta.xml              ← Canvas quiz settings
│       │   └── imsmanifest.xml                  ← standalone single-quiz manifest
│       └── [slug].zip                           ← built import (upload to Canvas)
├── _archive/                                    ← old/empty Canvas export artifacts
└── tasks/                                       ← per-session todos and lessons
```

**Source-of-truth rule:** `source.md` is the editable artifact. The QTI XML is a build output —
edit `source.md` and rebuild the package, not the other way around. Treat the GUID-named XML
files as artifacts.

**`source.md` structure** — see the template at `references/source-md-template.md`.

## Package Structure (one quiz, what gets zipped)

```
imsmanifest.xml                    ← standalone single-quiz manifest (one per zip)
[quiz-guid]/
  [quiz-guid].xml                  ← QTI 1.2 question data
  assessment_meta.xml              ← Canvas quiz settings
```

When inside the recommended layout above, this `imsmanifest.xml` lives alongside the QTI and meta
files inside the GUID folder, with hrefs that have no subfolder prefix (see `references/templates.md`
§ "Standalone folder manifest").

If adding to an existing package, append the new `<resource>` entries to the existing 
`imsmanifest.xml` rather than creating a new one.

## Step 0 — Generate a GUID

Every quiz and its dependency resource need unique GUIDs. Generate them with:

```bash
python3 -c "import secrets; print('g' + secrets.token_hex(16))"
```

Run this twice — once for the quiz GUID (used as folder name, XML filename, and `identifier` 
attribute), once for the dependency GUID (used only in the manifest `<dependency>` and the 
metadata resource `identifier`). A third GUID is needed for the `<assignment identifier=...>` 
inside `assessment_meta.xml`.

## Step 1 — imsmanifest.xml

See `references/templates.md` § imsmanifest for the full template.

Key rules:
- The manifest `identifier` attribute is its own unique GUID (not the quiz GUID).
- Each quiz contributes exactly two `<resource>` elements: one `imsqti_xmlv1p2` (the QTI file) 
  and one `associatedcontent/imscc_xmlv1p1/learning-application-resource` (the metadata file).
- File paths in `href` and `<file href=...>` are relative to the manifest's location.
  - Root-level manifest: `[quiz-guid]/[quiz-guid].xml`
  - Folder-level standalone manifest: `[quiz-guid].xml`

## Step 2 — assessment_meta.xml

See `references/templates.md` § assessment_meta for the full template.

Key fields to customize per quiz:
| Field | Notes |
|-------|-------|
| `<title>` | Quiz display name in Canvas |
| `<points_possible>` | Float, e.g. `20.0`. Should equal `questions × points_per_question`. |
| `<time_limit>` | Integer minutes. Omit the element entirely if no time limit. |
| `<allowed_attempts>` | Usually `1`. Use `-1` for unlimited. |
| `<shuffle_answers>` | `true` or `false` |
| `<show_correct_answers>` | `false` hides answers after submission |
| `<due_at>` / `<lock_at>` | ISO 8601, e.g. `2026-02-27T05:59:59`. Omit or leave empty for no date. |
| `<workflow_state>` (inside `<assignment>`) | `published` or `unpublished` |

The `identifier` attribute on `<quiz>` = the quiz GUID. The `identifier` on `<assignment>` 
= a separate unique GUID.

## Step 3 — [quiz-guid].xml (QTI Assessment)

See `references/templates.md` § QTI for per-question templates.

### Document skeleton

```xml
<?xml version="1.0" encoding="UTF-8"?>
<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd">
  <assessment ident="[QUIZ-GUID]" title="[Quiz Title]">
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>qmd_timelimit</fieldlabel>
        <fieldentry>[MINUTES]</fieldentry>
      </qtimetadatafield>
      <qtimetadatafield>
        <fieldlabel>cc_maxattempts</fieldlabel>
        <fieldentry>1</fieldentry>
      </qtimetadatafield>
    </qtimetadata>
    <section ident="root_section">
      <!-- questions go here -->
    </section>
  </assessment>
</questestinterop>
```

### Answer ID Convention

Answer IDs are 4-digit integers. Use a consistent pattern to avoid collisions:
- Question N answer IDs start at `N×100`, incrementing by 100 per choice.
- Q1 T/F: `1100` (True), `1200` (False)
- Q2 MC: `2100`, `2200`, `2300`, `2400`
- Q3 MC: `3100`, `3200`, `3300`, `3400`
- ...and so on.

Each question also needs its own item GUID (`<item ident=...>`) and an 
`assessment_question_identifierref` GUID — generate these or use a sequential pattern like 
`g01a8b3c4d5e6f7a8b9c0d1e2f3a4b5c6`.

### HTML encoding in question text

Question text lives in `<mattext texttype="text/html">`. HTML-encode these characters:
- `"` → `&amp;quot;` (note the double-encode: it's inside an XML attribute that contains HTML)
- `&` → `&amp;amp;`
- `<` → `&lt;`
- `>` → `&gt;`

Answer choices use `texttype="text/plain"` — no encoding needed beyond basic XML escaping.

## Authoring from a question list

When given questions in the format used in this course (like `quiz-questions-finals.md`):

```
True/False: [question text]. Answer: True/False ([optional clarification]).
Multiple Choice: [question text]
 A) ... B) ... C) ... D) ... Answer: [letter]
```

Map each question to its QTI item type:
- `True/False` → `true_false_question` with idents 1100/1200
- `Multiple Choice` with 4 options → `multiple_choice_question` with 4 `response_label` elements

The correct answer's ident goes in `<varequal respident="response1">` inside `<resprocessing>`.

## Verification checklist before handing off files

- [ ] Every GUID used in attributes is unique across the whole package
- [ ] `points_possible` in metadata = number of questions × points per question
- [ ] The `<varequal>` ident in `<resprocessing>` matches the correct answer's `<response_label ident>`
- [ ] `imsmanifest.xml` has a `<resource>` entry for both the QTI file and assessment_meta.xml
- [ ] File paths in manifest are relative and correct (subfolder vs. same-folder)
- [ ] HTML in `<mattext>` is properly encoded (quotes use `&amp;quot;`)

## Importing into Canvas

1. Zip the directory so `imsmanifest.xml` is at the zip root.
2. Canvas > Course > Settings > Import Course Content > Common Cartridge 1.x Package
3. Upload the zip. Canvas will show an import queue — quiz appears in Quizzes after completion.
