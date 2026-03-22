from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.autonomy_depth import (
    ensure_global_policy,
    initialize_repo_depth_state,
    required_context_files,
)


class AutonomyDepthTests(unittest.TestCase):
    def test_ensure_global_policy_seeds_policy_files(self) -> None:
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / ".claude"

            policy = ensure_global_policy(home)

            self.assertEqual(policy["user_max_depth"], 5)
            self.assertTrue((home / "policy" / "autonomy-depth.json").exists())
            self.assertTrue((home / "policy" / "required-context.json").exists())

    def test_initialize_repo_depth_state_uses_safe_default_for_normal_repo(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            repo.mkdir()
            (repo / ".brain" / "state").mkdir(parents=True)

            state = initialize_repo_depth_state(repo, {"user_max_depth": 5, "default_repo_start_depth": 2})

            self.assertEqual(state["current_depth"], 2)
            self.assertEqual(state["recommended_next_depth"], 3)
            self.assertEqual(state["allowed_max_depth"], 5)

    def test_required_context_files_expand_lead_department(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            repo.mkdir()

            ensure_global_policy(Path(tmp) / ".claude")
            files = required_context_files(
                repo,
                event="session-start",
                depth=3,
                lead_department="engineering",
                claude_home=Path(tmp) / ".claude",
            )

            self.assertIn(repo / ".claude" / "settings.local.json", files)
            self.assertIn(repo / ".claude" / "departments" / "engineering.md", files)
