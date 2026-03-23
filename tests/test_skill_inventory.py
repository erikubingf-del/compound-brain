from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.skill_inventory import refresh_repo_skill_state


class SkillInventoryTests(unittest.TestCase):
    def test_refresh_repo_skill_state_tracks_active_stale_missing_and_materialized_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "demo-repo"
            repo.mkdir()

            (repo / ".brain" / "knowledge" / "skills" / "patterns").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "departments").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(
                json.dumps(
                    {
                        "enabledDepartments": [
                            "architecture",
                            "engineering",
                            "operations",
                            "research",
                            "product",
                        ]
                    }
                )
            )
            (repo / "package.json").write_text("{}\n")
            (repo / "README.md").write_text("# Demo Repo\n")
            (repo / "src").mkdir()
            (repo / "src" / "App.tsx").write_text("export default function App() { return null; }\n")
            (repo / ".brain" / "knowledge" / "departments" / "engineering-sources.md").write_text(
                "# Engineering Department Sources\n\n"
                "## Objective\n"
                "- Deliver polished frontend implementation.\n\n"
                "## Approved Sources\n"
                "- curated-ui-repos\n\n"
                "## Search Queries\n"
                "- frontend design system\n"
                "- report export ui\n"
            )
            (repo / "tests").mkdir()
            (repo / ".github" / "workflows").mkdir(parents=True)
            (repo / ".brain" / "autoresearch" / "program.md").write_text("# Program\n")
            (repo / ".brain" / "knowledge" / "skills" / "skill-graph.md").write_text(
                "# Skill Graph\n\n"
                "## Debugging Reliability\n"
                "**Level:** Intermediate\n"
                "**Related Projects:** demo-repo\n"
                "**Key Knowledge:** Debugging code paths and improving reliability.\n"
                "**Next Improvements:** Connect reliability work to evaluations.\n\n"
                "## Legacy Terraform\n"
                "**Level:** Intermediate\n"
                "**Related Projects:** demo-repo\n"
                "**Key Knowledge:** Terraform module layout and infrastructure drift.\n"
                "**Next Improvements:** None.\n"
            )

            global_home = root / ".claude-home"
            (global_home / "knowledge" / "skills" / "patterns").mkdir(parents=True)
            (global_home / "knowledge" / "resources").mkdir(parents=True)
            (global_home / "knowledge" / "skills" / "skill-graph.md").write_text(
                "# Skill Graph\n\n"
                "## Release Operations\n"
                "**Level:** Advanced\n"
                "**Related Projects:** compound-brain\n"
                "**Key Knowledge:** Deploy, release, CI, and runtime safety controls.\n"
                "**Next Improvements:** Connect more repos to heartbeat review.\n"
            )
            (global_home / "knowledge" / "skills" / "patterns" / "release-operations.md").write_text(
                "# Release Operations\n\nUse guarded deploy and runtime review loops.\n"
            )
            (global_home / "knowledge" / "resources" / "skill-catalog.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "generated_at": "2026-03-23T12:00:00Z",
                        "candidates": [
                            {
                                "id": "github-report-crafter",
                                "title": "report-crafter",
                                "kind": "external-skill",
                                "source_type": "github",
                                "source_name": "acme/report-crafter",
                                "source_url": "https://github.com/acme/report-crafter",
                                "stars": 4200,
                                "updated_at": "2026-03-22T12:00:00Z",
                                "department_hints": ["product"],
                                "capability_hints": ["product-documentation"],
                                "summary": "High-quality report generation and document workflows.",
                                "candidate_tip": "Generate polished reports from validated project state.",
                                "source_trust": 0.88,
                                "freshness_days": 1,
                                "goal_fit": 0.84,
                                "confidence": 0.82,
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n"
            )
            (global_home / "knowledge" / "resources" / "project-tip-catalog.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "generated_at": "2026-03-23T12:00:00Z",
                        "tips": [
                            {
                                "id": "demo-repo-product-report-tip",
                                "source_repo": "demo-repo",
                                "department": "product",
                                "capability": "product-documentation",
                                "tip": "Use validated report structures and durable document templates.",
                                "evidence_count": 3,
                                "success_count": 2,
                                "failure_count": 1,
                                "last_seen": "2026-03-23T11:20:00Z",
                                "promotion_level": "repo-skill-candidate",
                                "confidence": 0.81,
                            }
                        ],
                    },
                    indent=2,
                )
                + "\n"
            )

            approved_root = root / "approved-skills"
            (approved_root / "ui-master").mkdir(parents=True)
            (approved_root / "ui-master" / "SKILL.md").write_text(
                "---\n"
                "name: ui-master\n"
                "description: Production-grade UI design and frontend implementation for React and Next.js.\n"
                "---\n"
            )

            state = refresh_repo_skill_state(
                repo,
                claude_home=global_home,
                approved_external_roots=[approved_root],
            )

            active_titles = {item["title"] for item in state["active"]}
            self.assertIn("Debugging Reliability", active_titles)
            self.assertIn("Release Operations", active_titles)
            self.assertIn("ui-master", active_titles)
            self.assertIn("Legacy Terraform", {item["title"] for item in state["stale"]})
            self.assertNotIn("Product Documentation", {item["title"] for item in state["missing"]})
            self.assertEqual(
                {item["title"] for item in state["materialized"]},
                {"Release Operations", "ui-master", "report-crafter"},
            )
            self.assertTrue(state["recommended"] or state["materialized"])
            shopping = json.loads((repo / ".brain" / "state" / "departments" / "engineering-shopping.json").read_text())
            self.assertTrue(shopping["candidate_skills"])
            candidate = shopping["candidate_skills"][0]
            self.assertIn("adaptation_notes", candidate)
            self.assertIn("source_trust", candidate)
            self.assertIn("freshness_days", candidate)
            self.assertIn("match_reasons", candidate)

            saved_state = json.loads((repo / ".brain" / "state" / "skills.json").read_text())
            self.assertEqual(saved_state["repo"], "demo-repo")
            self.assertEqual(saved_state["catalog_versions"]["skill_catalog"], 1)
            self.assertEqual(saved_state["catalog_versions"]["project_tip_catalog"], 1)
            self.assertTrue(saved_state["last_external_refresh"])
            self.assertTrue(saved_state["department_shopping"]["engineering"]["candidate_skills"])
            self.assertTrue(saved_state["department_shopping"]["product"]["adopted_skills"])
            self.assertTrue(
                (repo / ".brain" / "knowledge" / "skills" / "patterns" / "release-operations.md").exists()
            )
            self.assertTrue(
                (repo / ".brain" / "knowledge" / "skills" / "patterns" / "ui-master.md").exists()
            )
            self.assertTrue(
                (repo / ".brain" / "knowledge" / "skills" / "patterns" / "report-crafter.md").exists()
            )
            materialized_pattern = (
                repo / ".brain" / "knowledge" / "skills" / "patterns" / "ui-master.md"
            ).read_text()
            self.assertIn("## Repo Adaptation", materialized_pattern)
            product_candidate = saved_state["department_shopping"]["product"]["adopted_skills"][0]
            self.assertEqual(product_candidate["title"], "report-crafter")
