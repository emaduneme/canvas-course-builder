#!/usr/bin/env python3
"""Executable eval runner for canvas-course-builder.

Runs the design-spec §8 pipeline evals as real assertions against the reference
verifier and the research-provider resolver. Exits 0 only if every eval passes.

  python3 evals/run_evals.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIX = os.path.join(HERE, 'fixtures')
sys.path.insert(0, os.path.join(ROOT, 'skills', 'course-builder', 'scripts'))

import verify  # noqa: E402
from research_provider import resolve_provider  # noqa: E402

PROFILE = os.path.join(FIX, 'profile-valid.yml')
results = []


def record(name, ok, detail=''):
    results.append((name, ok, detail))


def run_verify(argv):
    """Invoke the verifier in-process; return (exit_code, report dict)."""
    import io
    import json
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = verify.main(argv)
    return code, json.loads(buf.getvalue())


def check(name, code, report, want_pass, must_fail_check=None):
    ok = (report['passed'] is want_pass) and (code == (0 if want_pass else 1))
    if must_fail_check and want_pass is False:
        failed = {c[0] for c in report['checks'] if not c[1]}
        ok = ok and (must_fail_check in failed)
    detail = report.get('disposition', '')
    record(name, ok, f"disposition={detail}")


# 1. profile parsing — valid
code, rep = run_verify(['--profile', PROFILE, '--kind', 'quiz',
                        '--source', os.path.join(FIX, 'quiz-good.md')])
check('profile_valid_parses + quiz-good passes', code, rep, want_pass=True)

# 2. profile parsing — null handling (template has all-null course/defaults sections)
tmpl = os.path.join(ROOT, 'templates', 'course-profile.template.yml')
try:
    parsed = verify.parse_yaml(open(tmpl).read())
    ok = (isinstance(parsed, dict)
          and parsed['course']['code'] is None
          and parsed['module_defaults'] is None
          and parsed['quiz_defaults']['time_limit'] is None)
    record('profile_null_handling (template all-null fields)', ok,
           'nulls preserved, not guessed')
except Exception as e:  # noqa: BLE001
    record('profile_null_handling (template all-null fields)', False, str(e))

# 3. profile parsing — malformed must be rejected (verifier returns code 1, profile_parsed False)
code, rep = run_verify(['--profile', os.path.join(FIX, 'profile-malformed.yml'),
                        '--kind', 'quiz', '--source', os.path.join(FIX, 'quiz-good.md')])
record('profile_malformed_rejected', code == 1 and rep.get('profile_parsed') is False,
       'verifier halts on unparseable profile')

# 4. traceability — untagged item must trigger halt
code, rep = run_verify(['--profile', PROFILE, '--kind', 'quiz',
                        '--source', os.path.join(FIX, 'quiz-untagged.md')])
check('untagged_item_triggers_halt', code, rep, want_pass=False,
      must_fail_check='every_item_tagged')
record('untagged_disposition_is_halt', rep['disposition'] == 'halt', rep['disposition'])

# 5. tag referencing nonexistent source_id must fail
code, rep = run_verify(['--profile', PROFILE, '--kind', 'quiz',
                        '--source', os.path.join(FIX, 'quiz-bad-source.md')])
check('bad_source_id_fails', code, rep, want_pass=False,
      must_fail_check='tags_reference_known_sources')

# 6. points-sum mismatch (quiz) must fail
code, rep = run_verify(['--profile', PROFILE, '--kind', 'quiz',
                        '--source', os.path.join(FIX, 'quiz-points-mismatch.md')])
check('quiz_points_mismatch_fails', code, rep, want_pass=False,
      must_fail_check='points_sum_matches')

# 7. rubric criteria sum to total_points (good) passes
code, rep = run_verify(['--profile', PROFILE, '--kind', 'rubric',
                        '--rubric', os.path.join(FIX, 'rubric-good.md')])
check('rubric_good_passes', code, rep, want_pass=True)

# 8. points-sum mismatch (rubric) must fail
code, rep = run_verify(['--profile', PROFILE, '--kind', 'rubric',
                        '--rubric', os.path.join(FIX, 'rubric-points-mismatch.md')])
check('rubric_points_mismatch_fails', code, rep, want_pass=False,
      must_fail_check='criteria_sum_to_total')

# 9. research fallback selects WebSearch when no Perplexity/Apify key present
record('research_fallback_websearch',
       resolve_provider(has_perplexity_key=False, has_apify=False) == 'websearch',
       'no keys -> websearch')
record('research_prefers_perplexity',
       resolve_provider(has_perplexity_key=True, has_apify=True) == 'perplexity',
       'key present -> perplexity')
record('research_apify_second',
       resolve_provider(has_perplexity_key=False, has_apify=True) == 'apify',
       'no perplexity, apify present -> apify')

# 10. empty-env sniff also yields websearch
record('research_fallback_empty_env',
       resolve_provider(env={}) == 'websearch', 'empty env -> websearch')


def main():
    width = max(len(n) for n, _, _ in results)
    npass = sum(1 for _, ok, _ in results if ok)
    print("canvas-course-builder — pipeline evals (§8)\n")
    for name, ok, detail in results:
        mark = 'PASS' if ok else 'FAIL'
        print(f"  [{mark}] {name.ljust(width)}  {detail}")
    print(f"\n{npass}/{len(results)} passed")
    return 0 if npass == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
