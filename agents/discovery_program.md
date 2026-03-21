# Discovery Agent — Autonomous Research Loop

> Copy this file as your program when running autonomous discovery for any project.
> Adapt the "Fixed evaluator" and "Mutable surface" sections to your project domain.

---

## What you are doing

You are the autonomous discovery agent. Your job: propose improvement candidates,
evaluate them against fixed criteria, and iterate until you find solutions that pass all gates.

**Domain-agnostic template** — fill in the `[PROJECT-SPECIFIC]` sections below.

---

## Fixed evaluator (DO NOT MODIFY)
`[PROJECT-SPECIFIC]` — specify what runs to evaluate a candidate:
```bash
# Example for a trading strategy project:
python3 research/evaluate.py > run.log 2>&1

# Example for a web app:
python3 -m pytest tests/ -q > run.log 2>&1

# Example for a data pipeline:
python3 validate_pipeline.py --candidate candidates.json > run.log 2>&1
```

## Mutable surface (the ONLY thing you change)
`[PROJECT-SPECIFIC]` — specify what file you edit per experiment:
- `candidates.json` — hypothesis list
- `src/feature_flag.py` — feature toggle
- `config/experiment.yaml` — experiment config

## Promotion gates (ALL must pass for KEEP)
`[PROJECT-SPECIFIC]` — fill in thresholds:
| Gate | Threshold |
|------|-----------|
| Primary metric | ≥ [threshold] |
| Statistical significance | p ≤ 0.05 |
| Sample size | ≥ [min_n] |
| Regression guard | No degradation on baseline |

---

## Loop workflow

### Setup (do once)
1. Read existing results to understand what already works
2. Create branch: `git checkout -b discovery/$(date +%Y%m%d)`
3. Verify mutable surface is reset to empty/baseline

### Experiment loop (repeat forever)
1. **Ideate** — Generate 3-5 new candidates not already tried
2. **Write** candidates to mutable surface
3. **Commit**: `git add [mutable] && git commit -m "research(candidates): [hypothesis]"`
4. **Run** the fixed evaluator
5. **Extract** key metrics from run.log
6. **If KEEP**: write board proposal to `.brain/knowledge/projects/board_proposal_YYYYMMDD.md`
7. **If DISCARD**: note why, adapt next hypothesis
8. **Clear** mutable surface
9. **Repeat**

---

## Results log (`results.tsv`)
| timestamp | candidate | metric_1 | metric_2 | status | notes |

---

## What NOT to do
- Do NOT modify the fixed evaluator
- Do NOT modify production configs
- Do NOT stop to ask permission
- Do NOT treat one KEEP as done
