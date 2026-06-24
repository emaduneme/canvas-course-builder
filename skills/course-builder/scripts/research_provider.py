#!/usr/bin/env python3
"""Research-source provider resolution (design spec §7).

Resolution order, each step gated on availability, degrading gracefully:
  1. Perplexity skill  — if PERPLEXITY/OpenRouter key configured (preferred, grounded+cited)
  2. Apify MCP         — if available (scraped/structured web sources)
  3. WebSearch         — always-available fallback, no key required

Kept as a tiny pure function so it is unit-testable by the eval runner.
"""
import os


def resolve_provider(has_perplexity_key=None, has_apify=None, env=None):
    """Return 'perplexity' | 'apify' | 'websearch'.

    Pass booleans explicitly (tests), or leave None to sniff the environment.
    """
    env = env if env is not None else os.environ
    if has_perplexity_key is None:
        has_perplexity_key = bool(
            env.get('PERPLEXITY_API_KEY') or env.get('OPENROUTER_API_KEY')
        )
    if has_apify is None:
        has_apify = bool(env.get('APIFY_TOKEN') or env.get('APIFY_API_TOKEN'))

    if has_perplexity_key:
        return 'perplexity'
    if has_apify:
        return 'apify'
    return 'websearch'


if __name__ == '__main__':
    import sys
    print(resolve_provider())
    sys.exit(0)
