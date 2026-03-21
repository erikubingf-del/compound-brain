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

