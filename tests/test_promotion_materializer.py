from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.promotion_materializer import apply_approved_candidates


class PromotionMaterializerTests(unittest.TestCase):
    def test_apply_approved_skill_candidate_updates_global_skill_graph(self) -> None:
        with TemporaryDirectory() as tmp:
            promotions = Path(tmp) / "promotions"
            knowledge = Path(tmp) / "knowledge"
            promotions.mkdir(parents=True, exist_ok=True)
            (promotions / "demo-skill.json").write_text(
                json.dumps(
                    {
                        "id": "demo-skill",
                        "source_repo": "demo",
                        "title": "Approval-gated orchestration",
                        "summary": "Reusable approval pattern",
                        "target_kind": "skills",
                        "status": "approved",
                        "skill_name": "Approval-gated orchestration",
                        "key_knowledge": "Require strategic approvals before autonomous shifts.",
                        "next_improvements": "Link approvals to department-specific evaluators.",
                        "pattern_body": "# Approval-gated orchestration\n\nUse approvals before strategic changes.\n",
                    },
                    indent=2,
                )
                + "\n"
            )

            result = apply_approved_candidates(promotions, knowledge)

            self.assertEqual(result["applied_count"], 1)
            graph = (knowledge / "skills" / "skill-graph.md").read_text()
            self.assertIn("Approval-gated orchestration", graph)
            payload = json.loads((promotions / "demo-skill.json").read_text())
            self.assertEqual(payload["status"], "applied")

    def test_apply_approved_qmp_candidate_writes_qmp_file_and_index(self) -> None:
        with TemporaryDirectory() as tmp:
            promotions = Path(tmp) / "promotions"
            knowledge = Path(tmp) / "knowledge"
            promotions.mkdir(parents=True, exist_ok=True)
            (promotions / "demo-qmp.json").write_text(
                json.dumps(
                    {
                        "id": "demo-qmp",
                        "source_repo": "demo",
                        "title": "How should promotion review be applied safely?",
                        "summary": "Promotion review should require explicit approval before landing in global knowledge.",
                        "target_kind": "qmp",
                        "status": "approved",
                        "question": "How should promotion review be applied safely?",
                        "model": "Use a review inbox and explicit approval before applying global knowledge changes.",
                        "process": "1. Review candidate. 2. Approve. 3. Apply to canonical knowledge.",
                    },
                    indent=2,
                )
                + "\n"
            )

            result = apply_approved_candidates(promotions, knowledge)

            self.assertEqual(result["applied_count"], 1)
            qmp_files = list((knowledge / "qmp").glob("qmp-*.md"))
            self.assertEqual(len(qmp_files), 1)
            self.assertIn("How should promotion review be applied safely?", qmp_files[0].read_text())
            self.assertIn("| 001 |", (knowledge / "qmp" / "_index.md").read_text())
