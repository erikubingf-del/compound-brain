# Activate Repo MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Claude-first `activate-repo` workflow that audits a repo, confirms strategic goals, materializes repo-local control surfaces, and starts bounded autonomous improvement loops backed by a shared `~/.claude` runtime.

**Architecture:** Keep shared orchestration in `~/.claude` while generating repo-local `.brain/` and `.claude/` surfaces per activated project. Drive all work through an activation state machine: preflight, audit, confirm, materialize, go live, and steady-state loops, with a global GitHub architecture radar feeding upgrades back into the shared runtime.

**Tech Stack:** Bash installer, Python 3 standard library, Markdown knowledge files, Claude Code hooks, cron, git worktrees/branches, unittest.

---

### Task 1: Build activation registry and preflight

**Files:**
- Create: `scripts/activate_repo.py`
- Create: `scripts/lib/__init__.py`
- Create: `scripts/lib/activation_registry.py`
- Create: `tests/test_activation_registry.py`
- Modify: `install.sh`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.activation_registry import ActivationRegistry


class ActivationRegistryTests(unittest.TestCase):
    def test_register_repo_records_alive_state(self) -> None:
        with TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "activated-projects.json"
            registry = ActivationRegistry(registry_path)
            record = registry.register_repo(
                repo_path="/tmp/demo",
                repo_name="demo",
                stack=["Python"],
                activation_mode="manual",
            )
            self.assertEqual(record["status"], "registered")
            stored = json.loads(registry_path.read_text())
            self.assertEqual(stored["projects"][0]["repo_name"], "demo")
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_activation_registry -v`
Expected: `FAILED` with `ModuleNotFoundError` or missing `ActivationRegistry`.

**Step 3: Write minimal implementation**

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ActivationRegistry:
    path: Path

    def register_repo(
        self,
        repo_path: str,
        repo_name: str,
        stack: list[str],
        activation_mode: str,
    ) -> dict:
        data = {"projects": []}
        if self.path.exists():
            data = json.loads(self.path.read_text())
        record = {
            "repo_path": repo_path,
            "repo_name": repo_name,
            "stack": stack,
            "activation_mode": activation_mode,
            "status": "registered",
        }
        data["projects"] = [p for p in data["projects"] if p["repo_path"] != repo_path]
        data["projects"].append(record)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2) + "\n")
        return record
```

**Step 4: Add CLI preflight entry point**

Implement `scripts/activate_repo.py` with:
- `--project-dir`
- `--check-only`
- detection for git root, stack, docs, tests, package manager, existing `.brain/`
  and `.claude/`
- registry write through `ActivationRegistry`
- stdout summary of detected surfaces and next activation state

**Step 5: Run test to verify it passes**

Run: `python3 -m unittest tests.test_activation_registry -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/activate_repo.py scripts/lib/__init__.py scripts/lib/activation_registry.py tests/test_activation_registry.py install.sh
git commit -m "feat(activation): add registry and preflight"
```

### Task 2: Generate audit packet and strategic confirmation state

**Files:**
- Modify: `scripts/project_auditor.py`
- Create: `scripts/lib/audit_packet.py`
- Create: `tests/test_audit_packet.py`
- Create: `brain-template/state/.gitkeep`

**Step 1: Write the failing test**

```python
import unittest

from scripts.lib.audit_packet import build_audit_packet


class AuditPacketTests(unittest.TestCase):
    def test_build_audit_packet_infers_departments(self) -> None:
        packet = build_audit_packet(
            repo_name="demo",
            tech_stack=["Python", "Docker"],
            docs_present=True,
            ci_present=True,
        )
        self.assertIn("architecture", packet["departments"])
        self.assertIn("engineering", packet["departments"])
        self.assertIn("project_goal_candidates", packet)
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_audit_packet -v`
Expected: `FAILED` because `build_audit_packet` does not exist.

**Step 3: Write minimal implementation**

```python
def build_audit_packet(
    repo_name: str,
    tech_stack: list[str],
    docs_present: bool,
    ci_present: bool,
) -> dict:
    departments = ["architecture", "engineering"]
    if docs_present:
        departments.append("product")
    if ci_present:
        departments.append("operations")
    return {
        "repo_name": repo_name,
        "project_goal_candidates": [f"Improve {repo_name} with autonomous guidance"],
        "departments": departments,
        "risks": [],
        "candidate_actions": [],
    }
```

**Step 4: Extend `project_auditor.py`**

Change audit output from a free-form report only to a structured packet that also
writes:
- `.brain/knowledge/audits/initial-audit.md`
- `.brain/state/goals.md`
- `.brain/state/audit-status.md`
- `.brain/state/action-queue.md`

Include a confirmation-ready section for:
- project goal candidates
- department list
- proposed architecture changes

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_audit_packet -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/project_auditor.py scripts/lib/audit_packet.py tests/test_audit_packet.py brain-template/state/.gitkeep
git commit -m "feat(audit): write activation audit packet"
```

### Task 3: Materialize repo-local `.claude/` and department surfaces

**Files:**
- Modify: `scripts/setup_brain.sh`
- Create: `scripts/materialize_project_claude.py`
- Create: `templates/project_claude/CLAUDE.md`
- Create: `templates/project_claude/settings.local.json`
- Create: `templates/project_claude/hooks/project_session_start.py`
- Create: `templates/project_claude/hooks/project_stop.py`
- Create: `templates/project_claude/hooks/project_llm_cron.py`
- Create: `templates/project_claude/departments/architecture.md`
- Create: `templates/project_claude/departments/engineering.md`
- Create: `templates/project_claude/departments/product.md`
- Create: `templates/project_claude/departments/research.md`
- Create: `tests/test_project_materialization.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.materialize_project_claude import materialize_project_claude


class ProjectMaterializationTests(unittest.TestCase):
    def test_materialize_project_claude_creates_hooks_and_departments(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            materialize_project_claude(repo, ["architecture", "engineering"])
            self.assertTrue((repo / ".claude" / "hooks" / "project_session_start.py").exists())
            self.assertTrue((repo / ".claude" / "departments" / "engineering.md").exists())
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_project_materialization -v`
Expected: `FAILED` because `materialize_project_claude` does not exist.

**Step 3: Write minimal implementation**

```python
from pathlib import Path


def materialize_project_claude(repo: Path, departments: list[str]) -> None:
    hooks_dir = repo / ".claude" / "hooks"
    dept_dir = repo / ".claude" / "departments"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    dept_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / "project_session_start.py").write_text("# generated\n")
    for department in departments:
        (dept_dir / f"{department}.md").write_text(f"# {department}\n")
```

**Step 4: Expand scaffolding**

Update `setup_brain.sh` and the new materializer so activation creates:
- `.brain/state/`
- repo `CLAUDE.md`
- `.claude/settings.local.json`
- `.claude/hooks/`
- `.claude/departments/`
- per-department goal placeholders and allowed-surface sections

**Step 5: Run test to verify it passes**

Run: `python3 -m unittest tests.test_project_materialization -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/setup_brain.sh scripts/materialize_project_claude.py templates/project_claude tests/test_project_materialization.py
git commit -m "feat(materialization): generate local claude control plane"
```

### Task 4: Add department goals and confidence-ranked action queues

**Files:**
- Modify: `scripts/probability_engine.py`
- Create: `scripts/lib/department_manager.py`
- Create: `scripts/lib/action_queue.py`
- Create: `tests/test_action_queue.py`

**Step 1: Write the failing test**

```python
import unittest

from scripts.lib.action_queue import rank_actions


class ActionQueueTests(unittest.TestCase):
    def test_rank_actions_prefers_high_alignment_and_confidence(self) -> None:
        ranked = rank_actions(
            [
                {"title": "rewrite docs", "goal_alignment": 4, "probability": 0.9, "urgency": 3, "cost": 2},
                {"title": "add gated activation", "goal_alignment": 9, "probability": 0.8, "urgency": 8, "cost": 3},
            ]
        )
        self.assertEqual(ranked[0]["title"], "add gated activation")
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_action_queue -v`
Expected: `FAILED` because `rank_actions` does not exist.

**Step 3: Write minimal implementation**

```python
def rank_actions(actions: list[dict]) -> list[dict]:
    def score(action: dict) -> float:
        return (
            action["goal_alignment"]
            * action["probability"]
            * action["urgency"]
            / max(action["cost"], 1)
        )

    ranked = []
    for action in actions:
        item = dict(action)
        item["score"] = round(score(action), 3)
        ranked.append(item)
    return sorted(ranked, key=lambda item: item["score"], reverse=True)
```

**Step 4: Integrate with activation flow**

Ensure the activation audit and steady-state loops write ranked actions to:
- `.brain/state/action-queue.md`
- `.claude/departments/<department>.md`

Add fields for:
- goal alignment
- evidence quality
- gating status
- recommended execution lane

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_action_queue -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/probability_engine.py scripts/lib/department_manager.py scripts/lib/action_queue.py tests/test_action_queue.py
git commit -m "feat(probability): rank department action queues"
```

### Task 5: Wire repo-local hooks and scheduled LLM loops

**Files:**
- Modify: `install.sh`
- Modify: `core/BRAIN.md`
- Create: `scripts/run_project_llm_cron.py`
- Create: `tests/test_install_dry_run.py`

**Step 1: Write the failing test**

```python
import subprocess
import unittest


class InstallDryRunTests(unittest.TestCase):
    def test_install_dry_run_mentions_activation_runtime(self) -> None:
        result = subprocess.run(
            ["bash", "install.sh", "--dry-run"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertIn("activate-repo", result.stdout)
        self.assertIn("registry", result.stdout)
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_install_dry_run -v`
Expected: `FAILED` because the installer output does not mention the new runtime.

**Step 3: Write minimal implementation**

Update `install.sh` so dry-run and real install both:
- create `~/.claude/registry/`
- install new activation/runtime scripts
- install shared hooks for session start, stop, and cron dispatch
- mention `activate-repo` as the primary workflow in stdout

Create `scripts/run_project_llm_cron.py` to dispatch scheduled repo-local loops
based on the activation registry and each repo's local `.claude/settings.local.json`.

**Step 4: Refresh the operating instructions**

Update `core/BRAIN.md` so session behavior reads:
- shared runtime from `~/.claude`
- repo-local hooks from `.claude/hooks/`
- activation-first workflow for making a repo alive

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_install_dry_run -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add install.sh core/BRAIN.md scripts/run_project_llm_cron.py tests/test_install_dry_run.py
git commit -m "feat(hooks): wire activation runtime and cron loops"
```

### Task 6: Add global GitHub architecture radar and orchestrator learning loop

**Files:**
- Modify: `scripts/github_intelligence.py`
- Create: `scripts/architecture_radar.py`
- Create: `tests/test_architecture_radar.py`
- Modify: `ARCHITECTURE.md`
- Modify: `README.md`

**Step 1: Write the failing test**

```python
import unittest

from scripts.architecture_radar import rank_findings


class ArchitectureRadarTests(unittest.TestCase):
    def test_rank_findings_prefers_goal_useful_patterns(self) -> None:
        ranked = rank_findings(
            [
                {"title": "flashy demo", "goal_fit": 2, "architecture_fit": 3, "confidence": 0.4},
                {"title": "gated planner loop", "goal_fit": 9, "architecture_fit": 8, "confidence": 0.8},
            ]
        )
        self.assertEqual(ranked[0]["title"], "gated planner loop")
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_architecture_radar -v`
Expected: `FAILED` because `architecture_radar.py` does not exist.

**Step 3: Write minimal implementation**

```python
def rank_findings(findings: list[dict]) -> list[dict]:
    def score(item: dict) -> float:
        return item["goal_fit"] * item["architecture_fit"] * item["confidence"]

    ranked = []
    for finding in findings:
        row = dict(finding)
        row["score"] = round(score(finding), 3)
        ranked.append(row)
    return sorted(ranked, key=lambda row: row["score"], reverse=True)
```

**Step 4: Integrate the radar**

The new radar should:
- scan configured GitHub sources or local result files
- write ranked recommendations to `~/.claude/knowledge/resources/architecture-radar.md`
- propose runtime improvements for the shared orchestrator
- optionally emit repo-level upgrade suggestions for alive repos

Update `README.md` and `ARCHITECTURE.md` to explain the architecture radar as a
core part of the product, not an optional side script.

**Step 5: Run tests**

Run: `python3 -m unittest tests.test_architecture_radar -v`
Expected: `OK`

**Step 6: Commit**

```bash
git add scripts/github_intelligence.py scripts/architecture_radar.py tests/test_architecture_radar.py README.md ARCHITECTURE.md
git commit -m "feat(radar): add global architecture learning loop"
```

### Task 7: Publish activation docs and verification path

**Files:**
- Modify: `README.md`
- Modify: `docs/CONTRIBUTING.md`
- Create: `examples/activate-repo-demo.md`
- Create: `tests/test_activate_repo_cli.py`

**Step 1: Write the failing test**

```python
import subprocess
import unittest


class ActivateRepoCliTests(unittest.TestCase):
    def test_activate_repo_help_lists_lifecycle_steps(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/activate_repo.py", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertIn("preflight", result.stdout.lower())
        self.assertIn("materialize", result.stdout.lower())
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_activate_repo_cli -v`
Expected: `FAILED` until the CLI help reflects the final lifecycle.

**Step 3: Write minimal implementation**

Update `scripts/activate_repo.py --help` and docs so the public flow is:
- install shared runtime
- run `activate-repo` in a repo
- review strategic confirmations
- let the repo go live

Document one end-to-end example in `examples/activate-repo-demo.md`.

**Step 4: Run final verification**

Run: `python3 -m unittest discover -s tests -p 'test_*.py' -v`
Expected: all new activation tests pass

Run: `bash install.sh --dry-run`
Expected: installer prints shared runtime, registry, hooks, and activation flow

**Step 5: Commit**

```bash
git add README.md docs/CONTRIBUTING.md examples/activate-repo-demo.md tests/test_activate_repo_cli.py scripts/activate_repo.py
git commit -m "docs(activation): publish activate-repo workflow"
```
