# Contributing to compound-brain

compound-brain is a system for making AI agents more effective over time.
Contributions that improve knowledge retention, session continuity, and
autonomous intelligence are most welcome.

---

## What's in scope

- Improvements to the `activate-repo` workflow
- Repo-local `.claude/` templates, departments, and hooks
- Global architecture radar and GitHub intelligence improvements
- New intelligence scripts (`scripts/`)
- New agent programs (`agents/`)
- New QMP seed entries (`knowledge-seed/qmp/`)
- Improvements to `core/BRAIN.md` operating instructions
- Improvements to `scripts/setup_brain.sh` scaffolding
- Bug fixes in `install.sh` or existing scripts
- Documentation and examples

## What's out of scope (for now)
- GUI or web dashboard
- Cloud sync or remote storage
- LLM provider integrations beyond the `claude` CLI

---

## Development setup

```bash
git clone https://github.com/your-username/compound-brain
cd compound-brain

# Test install in dry-run mode
bash install.sh --dry-run

# Test activate_repo on a scratch directory
mkdir /tmp/test-project && cd /tmp/test-project && git init
python3 /path/to/compound-brain/scripts/activate_repo.py --project-dir /tmp/test-project
```

---

## Adding a new intelligence script

1. Create `scripts/my_script.py`
2. Add it to the `SCRIPTS` array in `install.sh`
3. Add a cron entry in `install.sh` Step 6 (if periodic)
4. Document it in `ARCHITECTURE.md` under the Scripts table

Scripts should:
- Accept `--project-dir` as an argument
- Write output to `.brain/knowledge/daily/` or `.brain/knowledge/areas/`
- Respect `--dry-run` and `--check-only` modes where applicable
- Never modify production code, configs, or JSONL data files
- Handle missing `.brain/` gracefully (warn, don't crash)

## Adding a new agent program

1. Create `agents/my_program.md`
2. Follow the existing format: What you are doing → Fixed evaluator → Loop workflow → What NOT to do
3. Mark all project-specific sections as `[PROJECT-SPECIFIC]`
4. Add a row to the agent table in `core/BRAIN.md`

Agent programs must:
- Be domain-agnostic templates (project-specific parts are clearly marked)
- Operate in read-then-propose or read-then-alert mode for production systems
- Never modify production code or configs directly

## Adding a QMP seed entry

1. Create `knowledge-seed/qmp/qmp-NNN.md` (use the next available number)
2. Follow the Q / M / P / Applied To / Pitfalls structure
3. Add a row to `knowledge-seed/qmp/_index.md`

Good QMP seed entries are:
- Cross-project (applicable to most software projects)
- Process-level (not code-level — avoid language-specific snippets where possible)
- Learned from real incidents or repeated patterns

---

## Code style

- Shell scripts: `set -euo pipefail`, shellcheck-clean
- Python: standard library preferred, minimal third-party dependencies
- Markdown: CommonMark, no trailing whitespace, blank line before/after code blocks

---

## Pull requests

- Keep PRs small and focused — one feature or fix per PR
- Include a brief description of what changed and why
- If adding a script, include a `--dry-run` or `--check-only` mode where applicable
- Update `ARCHITECTURE.md` if you add a new component

---

## Reporting issues

Open a GitHub issue with:
- What you expected to happen
- What actually happened
- Output of `bash install.sh --dry-run` if the issue is install-related
- Your OS and shell (`uname -a`, `echo $SHELL`)
