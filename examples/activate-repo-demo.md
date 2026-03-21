# Activate Repo Demo

This example shows the intended activation flow for a single repo.

## 1. Install the shared runtime

```bash
git clone https://github.com/your-username/compound-brain
cd compound-brain
bash install.sh
```

## 2. Run activation inside a repo

```bash
cd /path/to/your/repo
python3 ~/.claude/scripts/activate_repo.py --project-dir .
```

The command should:
- run preflight
- infer starter departments
- scaffold `.brain/`
- materialize repo-local `.claude/`
- register the repo with the shared runtime

## 3. Review strategic confirmations

Activation should surface:
- project goal candidates
- department goals
- major architecture changes to confirm

## 4. Let the repo go live

Once confirmed, the repo should have:
- `.brain/` for persistent memory and state
- `.claude/` for repo-local hooks and departments
- ranked actions in `.brain/state/action-queue.md`
- department-level action context in `.claude/departments/*.md`
