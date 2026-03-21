# Activate Repo Autonomy Layer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the final autonomy model for `compound-brain`: a global orchestrator installed once, read-only previewing for non-activated repos, explicit `prepare-brain` and `activate-repo` steps for repo-local intelligence, and a self-hosting `compound-brain` repo that continuously improves itself with fixed evaluator gates.

**Architecture:** Separate global and repo mutation surfaces sharply. Build a global preview cache and promotion inbox in `~/.claude`, a static `prepare-brain` flow for `CLAUDE.md` + `.brain/` + `.codex/AGENTS.md`, and an `activate-repo` flow that adds `.claude/`, departments, approvals, hooks, skills, and autoresearch. Keep `compound-brain` itself always prepared and always activated, with self-improvement gated by `.brain/architecture/evaluator.md` and scorecards.

**Tech Stack:** Python 3, shell scaffolding, Markdown templates, JSON state files, unittest

---

### Task 1: Add global repo preview cache for observe and preview states

**Files:**
- Create: `scripts/lib/repo_preview_cache.py`
- Modify: `scripts/activate_repo.py`
- Create: `tests/test_repo_preview_cache.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.repo_preview_cache import RepoPreviewCache


class RepoPreviewCacheTests(unittest.TestCase):
    def test_upsert_preview_stores_goal_departments_and_commit(self) -> None:
        with TemporaryDirectory() as tmp:
            cache = RepoPreviewCache(Path(tmp) / "repo-previews.json")
            preview = cache.upsert_preview(
                repo_path="/tmp/demo",
                repo_name="demo",
                inferred_goal="Ship demo",
                departments=["engineering", "research"],
                risks=["Missing tests"],
                next_actions=["Prepare brain"],
                confidence=0.78,
                last_commit="abc123",
            )
            self.assertEqual(preview["repo_name"], "demo")
            self.assertEqual(preview["departments"], ["engineering", "research"])
            self.assertEqual(preview["last_commit"], "abc123")
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_repo_preview_cache -v`
Expected: `FAIL` because `RepoPreviewCache` does not exist.

**Step 3: Write minimal implementation**

Implement `RepoPreviewCache` with:

- `upsert_preview(...)`
- `load_preview(repo_path)`
- `list_due_previews(now)`

Store structured read-only preview state for non-activated repos in a JSON file
compatible with `~/.claude/registry/repo-previews.json`.

**Step 4: Integrate preview mode**

Update `scripts/activate_repo.py` or a small shared helper so the current
preflight path can also produce a read-only preview payload without writing repo
files.

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_repo_preview_cache tests.test_activate_repo_cli -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/lib/repo_preview_cache.py scripts/activate_repo.py tests/test_repo_preview_cache.py tests/test_activate_repo_cli.py
git commit -m "feat(preview): add global repo preview cache"
```

### Task 2: Add explicit `prepare-brain` flow for static project memory

**Files:**
- Create: `scripts/prepare_brain.py`
- Modify: `scripts/setup_brain.sh`
- Modify: `scripts/materialize_project_claude.py`
- Create: `templates/project_codex/AGENTS.md`
- Create: `tests/test_prepare_brain.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.prepare_brain import prepare_brain


class PrepareBrainTests(unittest.TestCase):
    def test_prepare_brain_writes_only_memory_and_codex_adapter(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            prepare_brain(repo)
            self.assertTrue((repo / "CLAUDE.md").exists())
            self.assertTrue((repo / ".brain").exists())
            self.assertTrue((repo / ".codex" / "AGENTS.md").exists())
            self.assertFalse((repo / ".claude").exists())
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_prepare_brain -v`
Expected: `FAIL` because `prepare_brain` does not exist.

**Step 3: Write minimal implementation**

Implement `prepare_brain(repo)` so it writes only:

- `CLAUDE.md`
- `.brain/`
- `.codex/AGENTS.md`

and explicitly avoids `.claude/`, departments, hooks, crons, approvals, and
autonomy state.

**Step 4: Run tests**

Run: `python3 -m unittest tests.test_prepare_brain tests.test_project_materialization -v`
Expected: `OK`

**Step 5: Commit**

```bash
git add scripts/prepare_brain.py scripts/setup_brain.sh scripts/materialize_project_claude.py templates/project_codex/AGENTS.md tests/test_prepare_brain.py tests/test_project_materialization.py
git commit -m "feat(prepare): add static project brain install"
```

### Task 3: Upgrade activation to build on prepared repos only

**Files:**
- Create: `scripts/lib/approval_state.py`
- Modify: `scripts/activate_repo.py`
- Create: `tests/test_approval_state.py`
- Create: `tests/test_activate_repo_cli.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.approval_state import ApprovalStateStore


class ApprovalStateTests(unittest.TestCase):
    def test_initialize_creates_pending_approval_for_activated_repo(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            state_dir = repo / ".brain" / "state"
            store = ApprovalStateStore(state_dir)
            state = store.initialize(
                project_goal_candidates=["Ship activation"],
                departments=["architecture", "engineering"],
            )
            self.assertEqual(state["state"], "awaiting-project-goal")
            self.assertIn("project_goal", state["pending"])
            self.assertIn("department_goals", state["pending"])
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_approval_state -v`
Expected: `FAIL` because `ApprovalStateStore` does not exist.

**Step 3: Write minimal implementation**

Implement `ApprovalStateStore` with:

- `initialize(...)`
- `load()`
- `record_transition(state, reason, pending)`
- file outputs:
  - `.brain/state/approval-state.json`
  - `.brain/state/pending-approvals.md`

**Step 4: Integrate activation**

Update `activate_repo.py` so activation:

- requires or creates a prepared brain first
- adds `.claude/`
- creates durable approval state
- leaves the repo in a pending strategic state until approved

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_approval_state tests.test_activate_repo_cli -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/lib/approval_state.py scripts/activate_repo.py tests/test_approval_state.py tests/test_activate_repo_cli.py
git commit -m "feat(activation): require prepared brain and approval state"
```

### Task 4: Materialize department contracts and activated repo state

**Files:**
- Create: `scripts/lib/department_state.py`
- Modify: `scripts/materialize_project_claude.py`
- Modify: `templates/project_claude/departments/architecture.md`
- Modify: `templates/project_claude/departments/engineering.md`
- Modify: `templates/project_claude/departments/product.md`
- Modify: `templates/project_claude/departments/research.md`
- Create: `tests/test_department_state.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.department_state import initialize_department_state


class DepartmentStateTests(unittest.TestCase):
    def test_initialize_department_state_creates_json_for_each_department(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            initialize_department_state(repo, ["architecture", "engineering"])
            state_path = repo / ".brain" / "state" / "departments" / "architecture.json"
            self.assertTrue(state_path.exists())
            payload = json.loads(state_path.read_text())
            self.assertEqual(payload["status"], "idle")
            self.assertEqual(payload["approval_state"], "pending")
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_department_state -v`
Expected: `FAIL` because department state initialization does not exist.

**Step 3: Write minimal implementation**

Create `initialize_department_state(repo, departments)` that writes one JSON
file per department with idle status, pending approval, empty current action,
and zeroed confidence.

**Step 4: Expand templates**

Update department templates so each file includes:

- mission
- department goal placeholder
- owned surfaces
- protected surfaces
- allowed actions
- evaluator/gates
- stop conditions
- escalation rules

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_department_state tests.test_project_materialization -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/lib/department_state.py scripts/materialize_project_claude.py templates/project_claude/departments/architecture.md templates/project_claude/departments/engineering.md templates/project_claude/departments/product.md templates/project_claude/departments/research.md tests/test_department_state.py tests/test_project_materialization.py
git commit -m "feat(departments): add activated repo department contracts"
```

### Task 5: Build the bounded department-cycle runtime

**Files:**
- Create: `scripts/lib/department_cycle.py`
- Modify: `scripts/run_project_llm_cron.py`
- Create: `tests/test_department_cycle.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.department_cycle import run_department_cycle


class DepartmentCycleTests(unittest.TestCase):
    def test_cycle_blocks_when_approval_is_pending(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "state" / "approval-state.json").write_text(
                json.dumps({"state": "awaiting-project-goal", "pending": ["project_goal"]})
            )
            result = run_department_cycle(repo, "architecture")
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["reason"], "approval-pending")
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_department_cycle -v`
Expected: `FAIL` because `run_department_cycle` does not exist.

**Step 3: Write minimal implementation**

Implement `run_department_cycle(repo, department)` with:

- approval check
- department spec load
- department state load
- one bounded action selection from action queue
- blocked result if strategic approval is pending

Return a structured result dict and update department state/log files.

**Step 4: Integrate cron**

Update `scripts/run_project_llm_cron.py` so an activated repo cron run:

- loads enabled departments from `.claude/settings.local.json`
- runs a bounded cycle per enabled department
- stops after the repo budget is exhausted
- writes run summaries into `.brain/knowledge/daily/YYYY-MM-DD.md`

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_department_cycle tests.test_activate_repo_cli -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/lib/department_cycle.py scripts/run_project_llm_cron.py tests/test_department_cycle.py tests/test_activate_repo_cli.py
git commit -m "feat(runtime): add bounded department cycle runner"
```

### Task 6: Add fixed-evaluator autoresearch program parsing

**Files:**
- Create: `scripts/lib/autoresearch_program.py`
- Modify: `scripts/materialize_project_claude.py`
- Create: `templates/project_claude/autoresearch/program.md`
- Create: `tests/test_autoresearch_program.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.autoresearch_program import load_autoresearch_program


class AutoresearchProgramTests(unittest.TestCase):
    def test_load_program_reads_required_contract_fields(self) -> None:
        with TemporaryDirectory() as tmp:
            program = Path(tmp) / "program.md"
            program.write_text(
                "# Program\n"
                "## Objective\nImprove test metric\n"
                "## Mutable Surfaces\n- src/core.py\n"
                "## Protected Surfaces\n- evaluator.py\n"
                "## Fixed Evaluator\npython3 eval.py\n"
                "## Run Command\npython3 eval.py\n"
                "## Keep/Discard Rule\nkeep on higher score\n"
            )
            data = load_autoresearch_program(program)
            self.assertEqual(data["objective"], "Improve test metric")
            self.assertIn("src/core.py", data["mutable_surfaces"])
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_autoresearch_program -v`
Expected: `FAIL` because the parser does not exist.

**Step 3: Write minimal implementation**

Create a parser that extracts and validates:

- objective
- mutable surfaces
- protected surfaces
- fixed evaluator
- run command
- metric extraction rule
- keep/discard rule
- runtime budget
- repair cap
- max iterations

**Step 4: Expand materialization**

If activation infers an autoresearch-eligible repo, materialize:

- `.brain/autoresearch/program.md`
- `.brain/autoresearch/queue.md`
- `.brain/autoresearch/results.jsonl`

Otherwise materialize only the directory and a placeholder contract.

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_autoresearch_program tests.test_project_materialization -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/lib/autoresearch_program.py scripts/materialize_project_claude.py templates/project_claude/autoresearch/program.md tests/test_autoresearch_program.py tests/test_project_materialization.py
git commit -m "feat(autoresearch): add program contract parsing"
```

### Task 7: Implement bounded autoresearch keep/discard execution

**Files:**
- Create: `scripts/lib/autoresearch_runner.py`
- Create: `tests/test_autoresearch_runner.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.autoresearch_runner import run_autoresearch_cycle


class AutoresearchRunnerTests(unittest.TestCase):
    def test_cycle_refuses_to_run_without_autoresearch_approval(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
            (repo / ".brain" / "state" / "approval-state.json").write_text(
                json.dumps({"state": "awaiting-autoresearch-enable", "pending": ["autoresearch_enable"]})
            )
            result = run_autoresearch_cycle(repo, "research")
            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["reason"], "autoresearch-not-approved")
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_autoresearch_runner -v`
Expected: `FAIL` because the runner does not exist.

**Step 3: Write minimal implementation**

Implement `run_autoresearch_cycle(repo, department)` with:

- approval check
- `program.md` load and validation
- baseline initialization if missing
- one queued experiment selection
- result append to `results.jsonl`
- `keep`, `discard`, or `crash` outcome handling

Keep git-mutating behavior behind a narrow helper so the first iteration can be
tested with dry-run or injected command runners.

**Step 4: Run tests**

Run: `python3 -m unittest tests.test_autoresearch_runner -v`
Expected: `OK`

**Step 5: Commit**

```bash
git add scripts/lib/autoresearch_runner.py tests/test_autoresearch_runner.py
git commit -m "feat(autoresearch): add bounded keep-discard runner"
```

### Task 8: Add project skill evolution and global promotion inbox

**Files:**
- Create: `scripts/lib/skill_evolution.py`
- Create: `scripts/lib/promotion_inbox.py`
- Modify: `scripts/run_project_llm_cron.py`
- Create: `tests/test_skill_evolution.py`
- Create: `tests/test_promotion_inbox.py`

**Step 1: Write the failing tests**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.skill_evolution import promote_skill_pattern
from scripts.lib.promotion_inbox import PromotionInbox


class SkillEvolutionTests(unittest.TestCase):
    def test_promote_skill_pattern_writes_pattern_and_updates_graph(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            graph = repo / ".brain" / "knowledge" / "skills" / "skill-graph.md"
            graph.parent.mkdir(parents=True, exist_ok=True)
            graph.write_text("# Skill Graph\n")
            promote_skill_pattern(
                repo=repo,
                skill_name="Approval-Gated Refactoring",
                related_projects=["demo"],
                key_knowledge="Only change owned surfaces after approval.",
                next_improvements="Tighten evaluator wiring.",
                pattern_body="# Pattern\n",
            )
            self.assertIn("Approval-Gated Refactoring", graph.read_text())


class PromotionInboxTests(unittest.TestCase):
    def test_submit_candidate_writes_global_review_entry(self) -> None:
        with TemporaryDirectory() as tmp:
            inbox = PromotionInbox(Path(tmp) / "promotions")
            record = inbox.submit_candidate(
                source_repo="demo",
                title="Approval-gated refactoring",
                summary="Reusable approval pattern",
                target_kind="skills",
            )
            self.assertEqual(record["status"], "pending-review")
```

**Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_evolution tests.test_promotion_inbox -v`
Expected: `FAIL` because the promotion helpers do not exist.

**Step 3: Write minimal implementation**

Implement:

- `promote_skill_pattern(...)` for project-local `skill-graph.md` and pattern
  files
- `PromotionInbox.submit_candidate(...)` for the global promotion inbox under
  `~/.claude/knowledge/promotions/`

**Step 4: Integrate runtime**

Update `run_project_llm_cron.py` so project skill promotion remains local, and
cross-project candidates are emitted into the global inbox instead of directly
editing global PARA/QMP/skills.

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_skill_evolution tests.test_promotion_inbox tests.test_department_cycle -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/lib/skill_evolution.py scripts/lib/promotion_inbox.py scripts/run_project_llm_cron.py tests/test_skill_evolution.py tests/test_promotion_inbox.py tests/test_department_cycle.py
git commit -m "feat(memory): add promotion inbox and skill evolution"
```

### Task 9: Add self-hosting evaluator surfaces for `compound-brain`

**Files:**
- Create: `.brain/architecture/evaluator.md`
- Create: `.brain/architecture/scorecard.json`
- Create: `scripts/lib/architecture_evaluator.py`
- Create: `tests/test_architecture_evaluator.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.architecture_evaluator import load_architecture_evaluator


class ArchitectureEvaluatorTests(unittest.TestCase):
    def test_load_evaluator_reads_protected_invariants_and_thresholds(self) -> None:
        with TemporaryDirectory() as tmp:
            evaluator = Path(tmp) / "evaluator.md"
            evaluator.write_text(
                "# Evaluator\n"
                "## Protected Invariants\n- Single repo control plane\n"
                "## Keep Thresholds\n- deterministic_gates: required\n"
            )
            data = load_architecture_evaluator(evaluator)
            self.assertIn("Single repo control plane", data["protected_invariants"])
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_architecture_evaluator -v`
Expected: `FAIL` because the evaluator loader does not exist.

**Step 3: Write minimal implementation**

Implement:

- evaluator loader/parser
- scorecard writer
- helper that records architecture scores without allowing automatic evaluator
  rewrites

**Step 4: Run tests**

Run: `python3 -m unittest tests.test_architecture_evaluator -v`
Expected: `OK`

**Step 5: Commit**

```bash
git add .brain/architecture/evaluator.md .brain/architecture/scorecard.json scripts/lib/architecture_evaluator.py tests/test_architecture_evaluator.py
git commit -m "feat(architecture): add self-hosting evaluator surfaces"
```

### Task 10: Wire self-hosting `compound-brain` loops and documentation

**Files:**
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `examples/activate-repo-demo.md`
- Modify: `docs/CONTRIBUTING.md`
- Modify: `install.sh`

**Step 1: Write the docs delta**

Document:

- global install vs repo activation
- observe/preview/prepare/activate lifecycle
- prepared repos staying static
- promotion inbox review
- self-hosting `compound-brain`
- architecture evaluator and approval-gated rubric changes

**Step 2: Update installer messaging**

Update `install.sh` output to describe:

- global orchestrator installation
- preview cache behavior
- `prepare-brain`
- `activate-repo`
- self-hosting behavior for `compound-brain`

**Step 3: Verify docs reference real files and commands**

Run: `rg -n "prepare-brain|observe|preview|promotion inbox|self-hosting|evaluator" README.md ARCHITECTURE.md examples/activate-repo-demo.md docs/CONTRIBUTING.md install.sh`
Expected: matches in each updated file.

**Step 4: Commit**

```bash
git add README.md ARCHITECTURE.md examples/activate-repo-demo.md docs/CONTRIBUTING.md install.sh
git commit -m "docs(activation): document final autonomy lifecycle"
```

### Task 11: Full verification sweep

**Files:**
- Verify only

**Step 1: Run focused test suite**

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v`
Expected: `OK`

**Step 2: Run installer dry-run**

Run: `bash install.sh --dry-run`
Expected: completes without errors and includes new preview/prepare/activate
messaging.

**Step 3: Run preview and prepare smoke test**

Run:

```bash
tmpdir=$(mktemp -d)
cd "$tmpdir"
git init -q
printf '# demo\n' > README.md
git add README.md
git commit -qm "init"
python3 /Users/erikfigueiredo/.config/superpowers/worktrees/compound-brain/codex-activate-repo-mvp/scripts/prepare_brain.py "$tmpdir"
find "$tmpdir/.brain" -maxdepth 3 -type f | sort
find "$tmpdir/.codex" -maxdepth 2 -type f | sort
test ! -d "$tmpdir/.claude"
```

Expected:

- prepare completes without crashing
- `.brain/` exists
- `.codex/AGENTS.md` exists
- `.claude/` does not exist

**Step 4: Run activation smoke test**

Run:

```bash
python3 /Users/erikfigueiredo/.config/superpowers/worktrees/compound-brain/codex-activate-repo-mvp/scripts/activate_repo.py --project-dir "$tmpdir"
find "$tmpdir/.claude" -maxdepth 3 -type f | sort
test -f "$tmpdir/.brain/state/approval-state.json"
```

Expected:

- activation completes without crashing
- `.claude/departments/*.md` exists
- `.brain/state/approval-state.json` exists

**Step 5: Commit final verification fixups if needed**

```bash
git add -A
git commit -m "test(activation): verify final autonomy lifecycle" || true
```
