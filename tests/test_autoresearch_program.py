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

