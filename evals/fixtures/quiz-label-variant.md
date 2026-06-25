# Eval Quiz — declared total under a label variant ("Points Possible")

# Regression guard for the parse_declared_points label-cell bug: the declared
# total (9) is read from a "Points Possible" row and is NOT equal to
# points_per_item * item_count (2 * 3 = 6). So this fixture only passes if the
# verifier actually reads the declared total from the label-variant cell.

## Settings

| Field | Value |
|---|---|
| Title | Label Variant Quiz |
| Points Possible | 9 |

## Questions

### Q1 (Multiple Choice) [src: syllabus §p.1] [points: 3]
Item one, worth 3.
- **A. ok** ✓
- B. no
- C. no
- D. no

### Q2 (Multiple Choice) [src: workbook-ch3 §p.42] [points: 3]
Item two, worth 3.
- **A. ok** ✓
- B. no
- C. no
- D. no

### Q3 (True/False) [src: pr-ethics §code-1] [points: 3]
Item three, worth 3.

**Answer: True** ✓
