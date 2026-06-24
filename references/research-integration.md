# Research integration — provider fallback contract (design spec §7)

When a `sources` entry has `type: research`, intake gathers grounding material and **caches it
to a local citeable file** (`cached_to`, i.e. `sources/<id>.md`) **before any question is
written**. This preserves the verifier invariant: every item must trace to a real, local
source. Questions cite the cached file; the cache cites the web.

## Resolution order

Each step is gated on availability and degrades gracefully. The logic is a tiny pure function in
`skills/course-builder/scripts/research_provider.py` (`resolve_provider`), unit-tested by the
eval runner:

1. **Perplexity skill** — preferred (grounded, cited answers). Selected when
   `PERPLEXITY_API_KEY` or `OPENROUTER_API_KEY` is set. Uses the existing `perplexity-search`
   skill if installed.
2. **Apify MCP** — for scraped/structured web sources. Selected when `APIFY_TOKEN` (or
   `APIFY_API_TOKEN`) is set and the Apify MCP server is connected.
3. **WebSearch** — always-available fallback, no key required. This is what a fresh clone of the
   plugin uses out of the box.

```python
resolve_provider(has_perplexity_key=False, has_apify=False) == 'websearch'
resolve_provider(has_perplexity_key=True,  has_apify=True)  == 'perplexity'
resolve_provider(has_perplexity_key=False, has_apify=True)  == 'apify'
```

With no explicit booleans, the function sniffs the environment variables above.

## Plugging in your own keys

| Provider | How to enable |
|---|---|
| Perplexity | `export PERPLEXITY_API_KEY=…` (or `OPENROUTER_API_KEY`); install the `perplexity-search` skill |
| Apify | `export APIFY_TOKEN=…`; connect the Apify MCP server |
| WebSearch | nothing — works by default |

## The cached source file

`sources/<id>.md` must be self-contained and citeable. Recommended shape:

```markdown
# <label> — researched <YYYY-MM-DD> via <provider>

> query: "<query>"

## Findings
… grounded notes the question-worker can draw from …

## Citations
1. <title> — <url> (accessed YYYY-MM-DD)
```

Because the file is local and concrete, `[src: <id> §<locator>]` tags on the resulting questions
resolve through the verifier exactly like any dropped file.
