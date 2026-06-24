#!/usr/bin/env python3
"""canvas-course-builder verifier (reference implementation).

Enforces the design-spec §6 invariants and emits a trace.json audit trail.
Pure stdlib — no PyYAML dependency (a YAML-subset parser is bundled below so the
plugin verifies out of the box on any machine with python3).

Usage:
  verify.py --profile PROFILE --kind quiz   --source SOURCE_MD [--points-possible N] [--out trace.json]
  verify.py --profile PROFILE --kind rubric --rubric RUBRIC   [--out trace.json]
  verify.py --profile PROFILE --kind qti    --package DIR      [--out trace.json]

Exit code: 0 if all checks pass, 1 if any check fails (regardless of
on_verify_fail — the orchestrator reads `disposition` to decide halt vs continue).
"""
import argparse
import json
import os
import re
import sys


# --------------------------------------------------------------------------- #
# YAML subset parser (maps, lists-of-maps, scalars, null/bool/int/float, flow lists)
# --------------------------------------------------------------------------- #
def _strip_comment(line):
    in_s = in_d = False
    out = []
    for i, c in enumerate(line):
        if c == "'" and not in_d:
            in_s = not in_s
        elif c == '"' and not in_s:
            in_d = not in_d
        elif c == '#' and not in_s and not in_d:
            if i == 0 or line[i - 1] in ' \t':
                break
        out.append(c)
    return ''.join(out).rstrip()


def _scalar(v):
    v = v.strip()
    if v == '':
        return None
    if (v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'"):
        return v[1:-1]
    if v in ('null', '~', 'Null', 'NULL'):
        return None
    if v in ('true', 'True', 'TRUE'):
        return True
    if v in ('false', 'False', 'FALSE'):
        return False
    if v.startswith('[') and v.endswith(']'):
        inner = v[1:-1].strip()
        return [_scalar(x) for x in inner.split(',')] if inner else []
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


class YAMLError(Exception):
    pass


def parse_yaml(text):
    raw = []
    for line in text.splitlines():
        s = _strip_comment(line)
        if s.strip() == '':
            continue
        indent = len(s) - len(s.lstrip(' '))
        raw.append((indent, s.strip()))
    pos = [0]

    def block():
        if pos[0] >= len(raw):
            return None
        _, content = raw[pos[0]]
        return parse_list() if content.startswith('- ') else parse_map()

    def parse_map():
        indent = raw[pos[0]][0]
        d = {}
        while pos[0] < len(raw):
            cind, content = raw[pos[0]]
            if cind < indent or content.startswith('- '):
                break
            if cind > indent or ':' not in content:
                raise YAMLError(f"bad map line: {content!r}")
            key, _, val = content.partition(':')
            key, val = key.strip(), val.strip()
            pos[0] += 1
            if val == '':
                if pos[0] < len(raw) and raw[pos[0]][0] > indent:
                    d[key] = block()
                else:
                    d[key] = None
            else:
                d[key] = _scalar(val)
        return d

    def parse_list():
        indent = raw[pos[0]][0]
        lst = []
        while pos[0] < len(raw):
            cind, content = raw[pos[0]]
            if cind != indent or not content.startswith('- '):
                break
            rest = content[2:].strip()
            pos[0] += 1
            if ':' in rest and not (rest.startswith('"') or rest.startswith("'")):
                item = {}
                k, _, v = rest.partition(':')
                k, v = k.strip(), v.strip()
                if v == '' and pos[0] < len(raw) and raw[pos[0]][0] > indent:
                    item[k] = block()
                else:
                    item[k] = _scalar(v)
                while (pos[0] < len(raw) and raw[pos[0]][0] > indent
                       and not raw[pos[0]][1].startswith('- ')):
                    cind2, content2 = raw[pos[0]]
                    k2, _, v2 = content2.partition(':')
                    k2, v2 = k2.strip(), v2.strip()
                    pos[0] += 1
                    if v2 == '' and pos[0] < len(raw) and raw[pos[0]][0] > cind2:
                        item[k2] = block()
                    else:
                        item[k2] = _scalar(v2)
                lst.append(item)
            else:
                lst.append(_scalar(rest))
        return lst

    try:
        return block()
    except YAMLError:
        raise
    except Exception as e:  # noqa: BLE001 — surface parse failures as YAMLError
        raise YAMLError(str(e))


# --------------------------------------------------------------------------- #
# Source.md parsing
# --------------------------------------------------------------------------- #
TAG_RE = re.compile(r'\[src:\s*([^\]\s]+)\s*([^\]]*)\]')
POINTS_RE = re.compile(r'\[points:\s*([0-9.]+)\s*\]')
ITEM_HEADER_RE = re.compile(r'^#{2,4}\s+(Q\d+)\b(.*)$')


def parse_source_items(text):
    """Return list of {item, source_id, locator, points(float|None), raw}."""
    items = []
    for line in text.splitlines():
        m = ITEM_HEADER_RE.match(line.strip())
        if not m:
            continue
        label, rest = m.group(1), m.group(2)
        tag = TAG_RE.search(rest)
        pts = POINTS_RE.search(rest)
        items.append({
            'item': label,
            'source_id': tag.group(1) if tag else None,
            'locator': (tag.group(2).strip() or None) if tag else None,
            'points': float(pts.group(1)) if pts else None,
            'raw': line.strip(),
        })
    return items


def parse_declared_points(text):
    """Pull the total from a Settings table row like `| Points | 20 (2 per question) |`."""
    for line in text.splitlines():
        if re.search(r'\|\s*Points\s*\|', line, re.I):
            m = re.search(r'\|\s*Points\s*\|\s*([0-9.]+)', line, re.I)
            if m:
                return float(m.group(1))
    return None


# --------------------------------------------------------------------------- #
# Rubric parsing (markdown table or yaml-ish list)
# --------------------------------------------------------------------------- #
def parse_rubric_criteria(path):
    """Return list of {criterion, points}. Supports a .yml criteria list or a
    markdown table whose first numeric column per row is the criterion points."""
    text = _read(path)
    if path.endswith('.yml') or path.endswith('.yaml'):
        data = parse_yaml(text)
        crit = data.get('criteria') if isinstance(data, dict) else data
        out = []
        for c in (crit or []):
            out.append({'criterion': c.get('name') or c.get('criterion'),
                        'points': _num(c.get('points'))})
        return out
    out = []
    for line in text.splitlines():
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not cells or re.match(r'^[-:\s]+$', cells[0]):
            continue
        if cells[0].lower() in ('criterion', 'criteria', 'name'):
            continue
        pts = None
        for c in cells[1:]:
            m = re.match(r'^([0-9.]+)$', c)
            if m:
                pts = float(m.group(1))
                break
        out.append({'criterion': cells[0], 'points': pts})
    return out


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #
def _read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def check_quiz(profile, source_path, points_possible):
    checks = []
    qd = (profile.get('quiz_defaults') or {}) if isinstance(profile, dict) else {}
    sources = {s['id'] for s in (profile.get('sources') or []) if isinstance(s, dict) and s.get('id')}
    tagging = (qd.get('source_tagging') or 'required')
    text = _read(source_path)
    items = parse_source_items(text)
    ppi = _num(qd.get('points_per_item'))

    checks.append(('items_found', len(items) > 0, f"{len(items)} item(s) parsed"))

    if tagging == 'required':
        untagged = [it['item'] for it in items if not it['source_id']]
        checks.append(('every_item_tagged', not untagged,
                       "all items carry a [src: …] tag" if not untagged
                       else f"untagged items: {', '.join(untagged)}"))
    bad = [f"{it['item']}→{it['source_id']}" for it in items
           if it['source_id'] and it['source_id'] not in sources]
    checks.append(('tags_reference_known_sources', not bad,
                   "all source ids exist in profile.sources" if not bad
                   else f"unknown source ids: {', '.join(bad)}"))

    item_pts = sum((it['points'] if it['points'] is not None else (ppi or 0)) for it in items)
    declared = points_possible
    if declared is None:
        declared = parse_declared_points(text)
    if declared is None and ppi is not None:
        declared = ppi * len(items)
    ok_sum = declared is not None and abs(item_pts - declared) < 1e-6
    checks.append(('points_sum_matches', ok_sum,
                   f"item points {item_pts} == points_possible {declared}" if ok_sum
                   else f"item points {item_pts} != points_possible {declared}"))
    return items, checks


def check_rubric(profile, rubric_path):
    checks = []
    rd = (profile.get('rubric_defaults') or {}) if isinstance(profile, dict) else {}
    total = _num(rd.get('total_points'))
    expected_count = rd.get('criteria_count')
    criteria = parse_rubric_criteria(rubric_path)

    checks.append(('criteria_found', len(criteria) > 0, f"{len(criteria)} criteria parsed"))
    if expected_count is not None:
        checks.append(('criteria_count_matches', len(criteria) == expected_count,
                       f"{len(criteria)} criteria == criteria_count {expected_count}"))
    missing = [c['criterion'] for c in criteria if c['points'] is None]
    checks.append(('every_criterion_has_points', not missing,
                   "all criteria have points" if not missing
                   else f"missing points: {', '.join(str(m) for m in missing)}"))
    crit_sum = sum(c['points'] or 0 for c in criteria)
    ok_sum = total is not None and abs(crit_sum - total) < 1e-6
    checks.append(('criteria_sum_to_total', ok_sum,
                   f"criteria sum {crit_sum} == total_points {total}" if ok_sum
                   else f"criteria sum {crit_sum} != total_points {total}"))
    items = [{'item': c['criterion'], 'source_id': None, 'locator': None,
              'points': c['points']} for c in criteria]
    return items, checks


def check_qti(package_dir):
    """Best-effort QTI structural checks on a built package directory."""
    checks = []
    xml_files = []
    for root, _, files in os.walk(package_dir):
        for f in files:
            if f.endswith('.xml'):
                xml_files.append(os.path.join(root, f))
    checks.append(('package_has_xml', bool(xml_files), f"{len(xml_files)} xml file(s)"))
    manifest = next((p for p in xml_files if os.path.basename(p) == 'imsmanifest.xml'), None)
    checks.append(('manifest_present', manifest is not None, "imsmanifest.xml found"))
    if manifest:
        man = _read(manifest)
        hrefs = re.findall(r'href="([^"]+)"', man)
        base = os.path.dirname(manifest)
        missing = [h for h in hrefs if not os.path.exists(os.path.join(base, h))]
        checks.append(('manifest_paths_resolve', not missing,
                       "all <file href> paths resolve" if not missing
                       else f"missing: {', '.join(missing)}"))
    qti = next((p for p in xml_files if p != manifest and 'assessment_meta' not in p), None)
    if qti:
        q = _read(qti)
        idents = re.findall(r'<item ident="([^"]+)"', q)
        checks.append(('unique_item_guids', len(idents) == len(set(idents)),
                       f"{len(idents)} items, {len(set(idents))} unique"))
        labels = set(re.findall(r'<response_label ident="([^"]+)"', q))
        correct = re.findall(r'<varequal respident="response1">([^<]+)</varequal>', q)
        bad = [c for c in correct if c not in labels]
        checks.append(('correct_idents_map', not bad,
                       "every varequal maps to a response_label" if not bad
                       else f"dangling idents: {', '.join(bad)}"))
    return [], checks


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(description="canvas-course-builder verifier")
    ap.add_argument('--profile', required=True)
    ap.add_argument('--kind', required=True, choices=['quiz', 'rubric', 'qti'])
    ap.add_argument('--source')
    ap.add_argument('--rubric')
    ap.add_argument('--package')
    ap.add_argument('--points-possible', type=float, default=None)
    ap.add_argument('--slug', default=None)
    ap.add_argument('--out', default=None)
    args = ap.parse_args(argv)

    report = {'kind': args.kind, 'slug': args.slug, 'checks': [], 'items': [],
              'passed': False, 'disposition': None, 'on_verify_fail': None}

    try:
        profile = parse_yaml(_read(args.profile))
        if not isinstance(profile, dict):
            raise YAMLError("profile is not a mapping")
        report['profile_parsed'] = True
    except (YAMLError, OSError) as e:
        report['profile_parsed'] = False
        report['checks'] = [['profile_parses', False, str(e)]]
        report['disposition'] = 'halt'
        _emit(report, args.out)
        return 1

    out = profile.get('output') or {}
    on_fail = out.get('on_verify_fail') or 'halt'
    report['on_verify_fail'] = on_fail

    if args.kind == 'quiz':
        if not args.source:
            ap.error("--source required for kind=quiz")
        items, checks = check_quiz(profile, args.source, args.points_possible)
    elif args.kind == 'rubric':
        if not args.rubric:
            ap.error("--rubric required for kind=rubric")
        items, checks = check_rubric(profile, args.rubric)
    else:
        if not args.package:
            ap.error("--package required for kind=qti")
        items, checks = check_qti(args.package)

    report['items'] = items
    report['checks'] = [list(c) for c in checks]
    report['passed'] = all(c[1] for c in checks)
    report['disposition'] = ('pass' if report['passed']
                             else ('flag_and_continue' if on_fail == 'flag_and_continue' else 'halt'))
    _emit(report, args.out)
    return 0 if report['passed'] else 1


def _emit(report, out_path):
    blob = json.dumps(report, indent=2)
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(blob + '\n')
    print(blob)


if __name__ == '__main__':
    sys.exit(main())
