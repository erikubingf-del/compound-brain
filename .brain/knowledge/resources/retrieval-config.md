# Retrieval Configuration — Weekly Digest Research Lane

## Current Heuristics

| Heuristic | Value | Rationale |
|-----------|-------|-----------|
| Lane count | 4 (GitHub trending, Claude ecosystem, community techniques, official docs) | Covers supply-side (repos), demand-side (community), and authoritative (official) |
| Candidates per run | 12–15 | Enough for meaningful coverage without context overflow |
| Dedup strategy | Read last 4 digests in `.brain/knowledge/research/`; skip anything already reported | Prevents weekly re-report of the same finds |
| Recency filter | Prefer items dated after last digest | Avoid stale finds |
| Confidence threshold | Only include items where the source can be named and partially verified | No anonymous "someone said" claims |
| Native feature rule | Any Claude Code native-feature claim must be verified against official docs or tagged `[UNVERIFIED]` | Prevents acting on third-party blog claims |

## When to Re-Evaluate

Re-evaluate this config when:
- The weekly digest consistently finds < 10 novel candidates (lanes may need updating)
- Official doc URL structure changes (breaks the `site:code.claude.com` lane)
- A new platform emerges as the primary community source (e.g., if awesome-claude-code moves to a different host)
- The dedup window (last 4 digests) produces false positives (re-reporting) or false negatives (missing resurfaced items)

## EvolveMem Pattern Note (2026-11-23)

EvolveMem (arXiv 2605.13941) suggests treating retrieval configuration as a search space that an LLM improves through AutoResearch. For this routine, the retrieval config above is the equivalent of EvolveMem's "retrieval settings." After any major architecture change, consider whether the 4-lane structure still covers the right search space, and log the rationale for any changes here.
