# Observe / Prepare / Activate Demo

## 1. Install the global orchestrator

```bash
git clone https://github.com/your-username/compound-brain
cd compound-brain
bash install.sh
```

## 2. Preview a repo without writing repo files

```bash
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/repo --check-only
```

This updates the global preview cache and prints:
- inferred goal
- proposed departments
- recommended next action

## 3. Prepare static project memory

```bash
python3 ~/.claude/scripts/prepare_brain.py /path/to/repo
```

This writes:
- `CLAUDE.md`
- `.brain/`
- `.codex/AGENTS.md`

It does not write:
- `.claude/`
- department hooks
- local cron/hook runtime

## 4. Activate full repo autonomy

```bash
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/repo
```

This adds:
- `.claude/settings.local.json`
- `.claude/departments/*.md`
- `.claude/hooks/*.py`
- `.brain/state/approval-state.json`
- `.brain/state/departments/*.json`
- `.brain/autoresearch/program.md`

The repo now has bounded local autonomy, but strategic approvals still gate
major direction changes.
