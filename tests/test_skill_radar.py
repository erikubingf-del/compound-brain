from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.skill_radar import refresh_skill_radar


class SkillRadarTests(unittest.TestCase):
    def test_refresh_skill_radar_writes_global_catalogs_and_project_tips(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude_home = root / ".claude"
            repo = root / "demo-repo"
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(
                json.dumps({"enabledDepartments": ["engineering", "product"]}) + "\n"
            )
            (repo / "package.json").write_text("{}\n")
            (repo / "README.md").write_text("# Demo Repo\n")
            (repo / "src").mkdir()
            (repo / "src" / "App.tsx").write_text("export default function App() { return null; }\n")
            (repo / ".brain" / "knowledge" / "departments").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "departments" / "engineering.md").write_text(
                "# Engineering Department Memory\n\n## Durable Lessons\n- Prefer typed UI actions.\n"
            )
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "state" / "operator-recommendation.json").write_text(
                json.dumps(
                    {
                        "lead_department": "engineering",
                        "rationale": ["recent UI regressions", "missing report generation skill"],
                    }
                )
                + "\n"
            )
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
            (repo / ".brain" / "autoresearch" / "results.jsonl").write_text(
                json.dumps({"status": "kept", "department": "research", "hypothesis": "Use structured exports"}) + "\n"
            )

            def fake_search(query: str, per_page: int = 3) -> list[dict]:
                return [
                    {
                        "full_name": "acme/report-crafter",
                        "html_url": "https://github.com/acme/report-crafter",
                        "description": f"Patterns for {query}",
                        "stargazers_count": 4200,
                        "updated_at": "2026-03-22T12:00:00Z",
                        "language": "TypeScript",
                    }
                ]

            result = refresh_skill_radar(claude_home=claude_home, project_dirs=[repo], github_search_fn=fake_search)

            self.assertTrue((claude_home / "knowledge" / "resources" / "skill-catalog.json").exists())
            self.assertTrue((claude_home / "knowledge" / "resources" / "project-tip-catalog.json").exists())
            self.assertTrue((claude_home / "knowledge" / "resources" / "skill-radar-latest.md").exists())
            self.assertGreaterEqual(len(result["skill_catalog"]["candidates"]), 1)
            self.assertGreaterEqual(len(result["project_tip_catalog"]["tips"]), 1)
            candidate = result["skill_catalog"]["candidates"][0]
            self.assertEqual(candidate["source_name"], "acme/report-crafter")
            tip = result["project_tip_catalog"]["tips"][0]
            self.assertEqual(tip["source_repo"], "demo-repo")
