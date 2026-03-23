from pathlib import Path
from tempfile import TemporaryDirectory
import tomllib
import unittest

from scripts.lib.codex_automations import ensure_managed_automations


class CodexAutomationsTests(unittest.TestCase):
    def test_ensure_managed_automations_creates_runtime_and_skill_radar_tasks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude_home = root / ".claude"
            codex_home = root / ".codex"
            repo_root = root / "compound-brain"
            repo_root.mkdir()
            (claude_home / "policy").mkdir(parents=True)

            created = ensure_managed_automations(
                codex_home=codex_home,
                claude_home=claude_home,
                repo_root=repo_root,
            )

            self.assertEqual(
                {item["id"] for item in created},
                {"compound-brain-runtime-heartbeat", "compound-brain-skill-radar"},
            )

            heartbeat = tomllib.loads(
                (codex_home / "automations" / "compound-brain-runtime-heartbeat" / "automation.toml").read_text()
            )
            self.assertEqual(heartbeat["name"], "Compound Runtime Heartbeat")
            self.assertIn("project_runtime_event.py --event cron --all-activated", heartbeat["prompt"])
            self.assertEqual(heartbeat["rrule"], "RRULE:FREQ=HOURLY;INTERVAL=6")
            self.assertEqual(heartbeat["status"], "ACTIVE")
            self.assertEqual(heartbeat["execution_environment"], "local")
            self.assertEqual([Path(item).resolve() for item in heartbeat["cwds"]], [repo_root.resolve()])

            radar = tomllib.loads(
                (codex_home / "automations" / "compound-brain-skill-radar" / "automation.toml").read_text()
            )
            self.assertEqual(radar["name"], "Compound Skill Radar")
            self.assertIn("skill_radar_refresh.py", radar["prompt"])
            self.assertEqual(radar["rrule"], "RRULE:FREQ=HOURLY;INTERVAL=12")
            self.assertEqual(radar["status"], "ACTIVE")
            self.assertEqual([Path(item).resolve() for item in radar["cwds"]], [repo_root.resolve()])
