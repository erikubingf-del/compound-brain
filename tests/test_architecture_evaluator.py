from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.architecture_evaluator import build_architecture_scorecard, load_architecture_evaluator


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

    def test_build_scorecard_keeps_when_gates_pass_and_baseline_is_pending(self) -> None:
        scorecard = build_architecture_scorecard(
            previous={"baseline": {"deterministic_gates": "pending", "architecture_rubric": "pending", "canary_behavior": "pending"}},
            deterministic_gate_results={"tests": True, "install": True},
            rubric_results={"Control-plane integrity": "pass", "Claude/Codex parity": "pass"},
            canary_behavior="pass",
        )

        self.assertEqual(scorecard["decision"], "keep")
        self.assertEqual(scorecard["baseline"]["deterministic_gates"], "pass")

    def test_build_scorecard_discards_on_rubric_regression(self) -> None:
        scorecard = build_architecture_scorecard(
            previous={
                "baseline": {"deterministic_gates": "pass", "architecture_rubric": "pass", "canary_behavior": "pass"},
                "details": {"architecture_rubric": {"Control-plane integrity": "pass"}},
            },
            deterministic_gate_results={"tests": True},
            rubric_results={"Control-plane integrity": "fail"},
            canary_behavior="pass",
        )

        self.assertEqual(scorecard["decision"], "discard")
