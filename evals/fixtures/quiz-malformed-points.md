# Eval Quiz — malformed points value must NOT crash the verifier

# Regression guard for the bare-float() crash: Q1 carries a malformed `[points: 2.5.0]`.
# The verifier must treat it as "no explicit points" (fall back to points_per_item=2),
# not raise ValueError. Item sum then = 2 + 2 + 2 = 6 == declared 6 -> passes cleanly.

## Settings

| Field | Value |
|---|---|
| Points | 6 (2 per question) |

## Questions

### Q1 (Multiple Choice) [src: syllabus §p.1] [points: 2.5.0]
Malformed points value on this header.
- **A. ok** ✓
- B. no
- C. no
- D. no

### Q2 (Multiple Choice) [src: workbook-ch3 §p.42] [points: 2]
Item two.
- **A. ok** ✓
- B. no
- C. no
- D. no

### Q3 (True/False) [src: pr-ethics §code-1] [points: 2]
Item three.

**Answer: True** ✓
